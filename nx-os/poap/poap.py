#!/bin/env python3
#md5sum="eb08329071ac99ccc2739640439152a3"
"""
If any changes are made to this script, please run the below command
in bash shell to update the above md5sum. This is used for integrity check.
f=poap_nexus_script.py ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i \
"s/^#md5sum=.*/#md5sum=\"$(md5sum $f.md5 | sed 's/ .*//')\"/" $f
"""

import glob
import os
import pkgutil
import re
import shutil
import signal
import sys
import syslog
import time
from time import gmtime, strftime
import tarfile
import errno
import yaml

try:
    import subprocess as sp
except ImportError:
    sp = None

try:
    from cisco import cli
    from cisco import transfer
    legacy = True
except ImportError:
    from cli import *
    legacy = False

"""
Increasing the script timeout to handle the legacy nxos
versions where upgrading will take time
"""
# script_timeout=1800
# --- Start of user editable settings ---
# Host name and user credential
# Add the install_path option to install licenses, rpms,
# and certificates through script from the path mentioned. 
# A file named <serial-number>.yaml is to be placed inside a folder named serial-number
# which has details of files to be installed for the particular box.
# eg. if option added is "install_path" : "/tftpboot/"
# expected file is /tftpboot/<serial-number>/<serial-number>.yaml
# Keywords to be used are Version, License, RPM, Certificate and Trustpoint.
# Version is a mandatory keyword and it should be 1 for this release.
# License : All the license files to be installed need to be listed in this
# section in proper yaml syntax. Path should be relative to install_path
# RPM : All rpm files to be installed need to be listed in this section in
# proper yaml syntax. Path should be relative to install_path
# Certificate: All certificate files and public key files which do not have a
# trustpoint associated need to be listed in this section in proper yaml syntax.
# These will only be copied to bootflash/poap_files/
# Trustpoint : All pkcs12 certificates obtained from CA and which need trustpoint to be
# configured need to be listed against the correct CA-trustpoint name for 
# the same certificate with passphrase in proper yaml syntax.
#
# Sample YAML file (name XYZ12345.yaml)
# ----------------------------------------------------------------------------
# Version: 1
# Certificate:
# - ssh_key1.pub
# - XYZ12345/nxapi_server_key.pem
# - XYZ12345/nxapi_server_cert.pem
# License:
# - XYZ12345/XYZ12345_1.lic
# - XYZ12345_2.lic
# RPM:
# - POAP_TPARTY_AND_PATCH_RPMS/chef-12.19.33-1.nexus7.x86_64.rpm
# - mtx-openconfig-vlan-1.0.0.206-9.3.5.lib32_n9000.rpm
# - POAP_TPARTY_AND_PATCH_RPMS/nxos.POAP_SMU_BGP_RELOAD-n9k_ALL-1.0.0-9.3.5.lib32_n9000.rpm
# Target_image: nxos.9.3.5.bin
# Trustpoint:
#   Z1_TP:
#     POAP_TP_FILES/XYZ12345/Z1_TP.pfx: passphrase1
#   Z2_TP:
#     POAP_TP_FILES/XYZ12345/Z2_TP.p12: passphrase2
# ----------------------------------------------------------------------------
# Additionally a "Target_image" can also be defined in .yaml file for a box to override the
# target image for that specific box as opposed to the target_system_image given as common to all boxes
# through script. If Target_image mentioned in yaml then that image should be kept only in 
# target_system_image path mentioned within poap script. No relative path support for Target_image in yaml file

options = {
   "username": "root",
   "password": "password",
   "hostname": "2.1.1.1",
   "transfer_protocol": "scp",
   "mode": "serial_number",
   "target_system_image": "nxos.9.3.1.bin",
}

"""
Setting global_use_kstack to True makes copy operation use the 
kstack option to copy images.
Setting global_upgrade_bios to True makes sure BIOS gets upgraded
to latest BIOS available with the new image.
"""
global_use_kstack = False
global_upgrade_bios = False
global_copy_image = True

def download_scripts_and_agents():
    """
    Downloads user scripts, agents, and data after downloading config, but before installing
    the target image.  If an application is to be installed in the native Linux environment,
    uncomment and update the call to install_shell_script() as needed.
    The parameters are as follows:
        source_path: the server path or source path where the source file lives (e.g. /tftpboot)
        source_file: the name of the file on the server / source to download (e.g. agents.tar)
        dest_path: optional (defaults to /bootflash) parameter to specify where to download to
                   any intermediate directories will automatically be created.
        dest_file: optional (defaults to same name as source) parameter to specify the target name
        unpack: optional (defaults to False) parameter specifying if we should attempt to extract
                this file. The command 'tar -xf <target> -C /bootflash' is used for extraction.
        delete_after_unpack: optional (defaults to False) parameter specifying that we delete
                             the target file after successful extraction.
    """
    source_location = options["user_app_path"]
    # poap_log("Downloading scripts and agents from %s" % source_location)

    """
    Download the agent "monitor_dummy.py" from options["user_app_path"] to
     /bootflash/monitor_agent and rename it to "monitor_agent.py"
    """
    # download_user_app(source_location, "monitor_dummy.py", "/bootflash/monitor_agent/",
    #                  "monitor_agent.py")

    """
    Download a tarball containing several agents from /var/lib/tftpboot/agent_bundles to
    /bootflash/agent_root; don't rename the tarball.  Then unpack this tarball
     (tar -xf <tarball> -C /bootflash). If the tarball contains a directory called "agents" with
     3 agents inside of it, they will be unpacked to /bootflash/agents. Delete the tarball
     after successfully extracting the files.
    """
    # download_user_app("/var/lib/tftpboot/agent_bundles", "agent_directory.tar",
    #                    "/bootflash/agent_root", unpack=True, delete_after_unpack=True)

    """
    Download a shell script / agent called bootflash_agent.sh from options["user_app_path"]
     to /bootflash. Leave it named "bootflash_agent.sh"
    """
    # download_user_app(source_location, "bootflash_agent.sh")

    """
    Download a shell script / agent called "bootflash_agent.sh" from options["user_app_path"]
     to /bootflash, but rename it "different_name_agent.sh"
    """
    # download_user_app(source_location, "bootflash_agent.sh", "/bootflash",
    #                  "different_name_agent.sh")

    """
    Install a shell script that has already been downloaded
    """
    # install_shell_script("/bootflash", "poap_install")


def download_user_app(source_path, source_file, dest_path="/bootflash", dest_file="", unpack=False,
                      delete_after_unpack=False):
    """
    Downloads a user application, script, or data item.
    source_path: the source directory the file we want to download resides in
    source_file: the source file to download
    dest_path: optional parameter specifying where we want to copy the file to
    dest_file: optional parameter specifying what we want to name the file after we copy it
    unpack: optional boolean parameter specifying if we want to attempt to extract this file
    delete_after_unpack: optional boolean parameter specifying if we want to delete the tarball
    """
    # If the user doesn't specify the destination filename, use the same one as the source
    if dest_file == "":
        dest_file = source_file

    src = os.path.join(source_path, source_file)
    dst = os.path.join(dest_path, dest_file)

    tmp_file = "%s.tmp" % dst

    # Create intermediate directories if required for agents
    try:
        os.makedirs(dest_path)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(dest_path):
            raise

    do_copy(src, dst, options["timeout_copy_user"], tmp_file)

    if unpack is True:
        poap_log("Unpacking %s to /bootflash" % dst)

        unpack_success = False
        # Before Python 2.7 (no subprocess module at all)
        if sp is None:
            try:
                os.system("tar -xf %s -C /bootflash" % dst)
                unpack_success = True
            except Exception as e:
                poap_log("Failed to unpack %s: %s" % (dst, str(e)))
        else:
            try:
                out = sp.check_output("tar -xf %s -C /bootflash" % dst, shell=True,
                                      stderr=sp.STDOUT)
                unpack_success = True
            except AttributeError as e:
                try:
                    os.system("tar -xf %s -C /bootflash" % dst)
                    unpack_success = True
                except Exception as e:
                    poap_log("Failed to unpack %s: %s" % (dst, str(e)))
            except OSError as e:
                poap_log("Failed to unpack %s: %s" % (dst, str(e)))
            except sp.CalledProcessError as e:
                poap_log("Failed to unpack %s: %s (%s)" % (dst, str(e), e.output))

        # Now that we know we extracted the contents, cleanup the tarball
        if unpack_success is True and delete_after_unpack is True:
            remove_file(dst)


def install_shell_script(source_path, source_file):
    """
    Install a user shell script.
    The users's shell script is copied to /etc/init.d, and chkconfig is run
    so that the user's script will get executed when the switch boots.
    source_path: the source directory the file we want to install resides in
    source_file: the source file to install
    """

    fullpath = os.path.join(source_path, source_file)

    poap_log("Installing %s" % fullpath)

    try:
        os.system("cp %s /etc/init.d" % fullpath)
    except Exception as e:
        poap_log("Failed to copy %s: %s" % (fullpath, str(e)))
    else:
        poap_log("Copy %s to /etc/init.d succeeded" % fullpath)

    for i in range (0, 10):
        try:
            os.system("/usr/sbin/chkconfig --add %s" % source_file)
        except Exception as e:
            poap_log("Failed to chkconfig add %s: %s" % (source_file, str(e)))
        else:
            poap_log("Chkconfig add %s succeeded" % source_file)
            if (os.system("ls /etc/rc3.d/*%s" % source_file) == 0):
                poap_log("Chkconfig file exists, exiting retry loop")
                break
            else:
                poap_log("Chkconfig file does not exist, sleeping and looping")
                time.sleep(2)

    for i in range (0, 10):
        try:
            os.system("/usr/sbin/chkconfig --level 3 %s on" % source_file)
        except Exception as e:
            poap_log("Failed to chkconfig level 3 %s on: %s" % (source_file, str(e)))
        else:
            poap_log("Chkconfig level 3 %s on succeeded" % source_file)
            if (os.system("ls /etc/rc3.d/*%s" % source_file) == 0):
                poap_log("Chkconfig file exists, exiting retry loop")
                break
            else:
                poap_log("Chkconfig file does not exist, sleeping and looping")
                time.sleep(2)

    os.system("sync")
    time.sleep(5)

def set_defaults_and_validate_options():
    """
    Sets all the default values and creates needed variables for POAP to work.
    Also validates that the required options are provided
    """
    global options

    # Initialize globals
    init_globals()

    # Required parameters
    if "options" not in globals():
        abort("Options dictionary was not defined!")

    # Check which mode we're using
    if options.get("mode", "") == "personality":
        required_parameters = set()
    else:
        required_parameters = set(["target_system_image"])

    # USB doesn't require remote credentials
    if os.environ.get("POAP_PHASE", None) != "USB":
        # Remote download needs more parameters
        required_parameters.add("username")
        required_parameters.add("password")
        required_parameters.add("hostname")

    # If we are missing any required parameters
    missing_parameters = required_parameters.difference(list(options.keys()))
    if len(missing_parameters) != 0:
        poap_log("Required parameters are missing:")
        abort("Missing %s" % ", ".join(missing_parameters))

    # Set the POAP mode
    set_default("mode", "serial_number")

    # Required space to copy config kickstart and system image in KB
    set_default("required_space", 100000)
    # Transfer protocol (http, ftp, tftp, scp, etc.)
    set_default("transfer_protocol", "scp")
    # Directory where the config resides
    set_default("config_path", "/var/lib/tftpboot/")
    # Target image and its path (single image is default)
    set_default("target_system_image", "")
    set_default("target_image_path", "/var/lib/tftpboot/")
    set_default("target_kickstart_image", "")
    # Destination image and its path
    set_default("destination_path", "/bootflash/")
    set_default("destination_system_image", options["target_system_image"])
    set_default("destination_kickstart_image", options["target_kickstart_image"])
    set_default("destination_midway_system_image", "midway_system.bin")
    set_default("skip_multi_level", False)
    set_default("destination_midway_kickstart_image", "midway_kickstart.bin")
    set_default("serial_number","");
    set_default("install_path", "")
    set_default("use_nxos_boot", False)
    set_default("https_ignore_certificate", False)
    
    # User app path
    set_default("user_app_path", "/var/lib/tftpboot/")

    # MD5 Verification
    set_default("disable_md5", False)

    # Midway system and kickstart source file name.
    # This should be a 6.x U6 or greater dual image.
    # Required only if moving from pre 6.x U6 image to 7.x/higher image.
    set_default("midway_system_image", "")
    set_default("midway_kickstart_image", "")
    set_default("skip_multi_level", False)
    # --- USB related settings ---
    # USB slot info. By default its USB slot 1, if not specified specifically.
    # collina2 has 2 usb ports. To enable poap in usb slot 2 user has to set the
    # value of usbslot to 2.
    set_default("usb_slot", 1)
    # Source file name of Config file
    set_default("source_config_file", "poap.cfg")

    set_default("vrf", os.environ['POAP_VRF'])
    set_default("destination_config", "poap_conf.cfg")
    set_default("split_config_first", "poap_1.cfg")
    set_default("split_config_second", "poap_2.cfg")

    # Timeout info (in seconds)
    # Not applicable for TFTP protocol. POAP script timeout can help
    # in the case of TFTP.
    set_default("timeout_config", 120)  # 2 minutes
    set_default("timeout_copy_system", 2100)  # 35 minutes
    set_default("timeout_copy_kickstart", 900)  # 15 minutes
    set_default("timeout_copy_personality", 900)  # 15 minutes
    set_default("timeout_copy_user", 900)  # 15 minutes

    # Personality
    set_default("personality_path", "/var/lib/tftpboot")
    set_default("source_tarball", "personality.tar")
    set_default("destination_tarball", options["source_tarball"])
    set_default("compact_image", False)

    # Check that options are valid
    validate_options()

    
def validate_options():
    """
    Validates that the options provided by the user are valid.
    Aborts the script if they are not.
    """
    if os.environ.get("POAP_PHASE", None) == "USB" and options["mode"] == "personality":
        abort("POAP Personality is not supported via USB!")
        
    os.system("rm -rf /bootflash/poap_files")
    os.system("rm -rf /bootflash_sup-remote/poap_files")
    # Compare the list of what options users have to what options we actually support.
    supplied_options = set(options.keys())
    # Anything extra shouldn't be there
    invalid_options = supplied_options.difference(valid_options)
    for option in invalid_options:
        poap_log("Invalid option detected: %s (check spelling, capitalization, and underscores)" %
                 option)
    if len(invalid_options) > 0:
        abort()


def set_default(key, value):
    """
    Sets a value in the options dictionary if it isn't already set by the user
    """
    global options
    global valid_options

    if key not in options:
        options[key] = value

    # Track this is a valid option so we can validate that customers didn't
    # mistype any options
    valid_options.add(key)

def byte2str(byte_str):
    '''Ensuring python2 to python3 compatibility for subprocess outputs'''
    try:
        byte_str = byte_str.decode()
    except (UnicodeDecodeError, AttributeError):
        pass
    return byte_str

def rollback_rpm_license_certificates():
    '''Rolling back installed rpms,licenses and certificates during abort'''
    try:
        fpx = open("/bootflash/poap_files/success_install_list")
    except:
        return
    version = get_version()
    image_parts = [part for part in re.split("[\.()]", version) if part]
    rollback_files = fpx.readlines()
    for file in rollback_files:
        file = file.strip('\n')
        if file.endswith(".rpm"):
            group_string = "/usr/bin/rpm -qp --qf %{GROUP} /bootflash/poap_files/" + file
            rpm_string = "/usr/bin/rpm -qp --queryformat %{NXOSRPMTYPE} /bootflash/poap_files/" + file
            rpmgrp = subprocess.check_output(group_string, shell=True)
            rpmtype = subprocess.check_output(rpm_string, shell=True)
            rpmgrp = byte2str(rpmgrp)
            rpmtype = byte2str(rpmtype)
            if (len(rpmgrp) != 0 and 'Patch-RPM' in rpmgrp):
                poap_log("Rolling back patch RPM %s" %(file))
                os.system("rm -rf /bootflash/.rpmstore/patching/patchrepo/%s" %file)
                os.system("rm -rf /bootflash_sup-remote/.rpmstore/patching/patchrepo/%s" %file)
                removal_entry = file.replace(".rpm", "")
                entry_removal_string = "sed -i 's/ {0}//g' /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf".format(removal_entry)
                standby_removal_string = "sed -i 's/ {0}//g' /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf".format(removal_entry)
                os.system(entry_removal_string)               
                os.system(standby_removal_string)
                if(int(image_parts[0]) >= 10):
                    os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/patching/patchrepo/")
                    os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/patching/patchrepo/")
                else:                
                    os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash/.rpmstore/patching/patchrepo/")
                    os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash_sup-remote/.rpmstore/patching/patchrepo/")
            else:
                if (len(rpmtype) != 0 and 'feature' in rpmtype):
                    poap_log("Rolling back NXOS RPM %s" %(file))
                    os.system("rm -rf /bootflash/.rpmstore/patching/localrepo/%s" %file)
                    os.system("rm -rf /bootflash_sup-remote/.rpmstore/patching/localrepo/%s" %file)
                    if(int(image_parts[0]) >= 10):
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/patching/localrepo/")
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/patching/localrepo/")
                    else:                       
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash/.rpmstore/patching/localrepo/")          
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash_sup-remote/.rpmstore/patching/localrepo/")
                else:
                    poap_log("Rolling back thirdparty RPM %s" %(file))
                    os.system("rm -rf /bootflash/.rpmstore/thirdparty/%s" %file)      
                    os.system("rm -rf /bootflash_sup-remote/.rpmstore/thirdparty/%s" %file)            
                    if(int(image_parts[0]) >= 10):
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/thirdparty/")
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/thirdparty/")
                    else:                     
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash/.rpmstore/thirdparty/")
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash_sup-remote/.rpmstore/thirdparty/")
            poap_log("Removal of RPM names from nxos_rpms_persisted list")
            rpm_name = subprocess.check_output("/usr/bin/rpm -qp --qf %%{NAME} /bootflash/poap_files/%s" %file, shell=True)
            rpm_name = byte2str(rpm_name)
            rpm_persisted_removal_string = "sed -i '/^{0}$/d' /bootflash/.rpmstore/nxos_rpms_persisted" .format(rpm_name)
            standby_persisted_removal_string = "sed -i '/^{0}$/d' /bootflash_sup-remote/.rpmstore/nxos_rpms_persisted" .format(rpm_name)
            os.system(rpm_persisted_removal_string)
            os.system(standby_persisted_removal_string)
    os.system("rm -rf /bootflash/poap_files")
    standby = cli("show module | grep ha-standby")
    if(len(standby) > 0):
        os.system("rm -rf /bootflash_sup-remote/poap_files") 

def abort(msg=None):
    """
    Aborts the POAP script execution with an optional message.
    """
    global log_hdl

    if msg is not None:
        poap_log(msg)
    
    rollback_rpm_license_certificates()
    cleanup_files()
    close_log_handle()
    exit(1)


def close_log_handle():
    """
    Closes the log handle if it exists
    """
    if "log_hdl" in globals() and log_hdl is not None:
        log_hdl.close()


def init_globals():
    """
    Initializes all the global variables that are used in this POAP script
    """
    global log_hdl, syslog_prefix
    global empty_first_file, single_image, multi_step_install
    global valid_options
    global del_system_image, del_kickstart_image

    # A list of valid options
    valid_options = set(["username", "password", "hostname"])
    log_hdl = None
    syslog_prefix = ""
    # indicates whether first config file is empty or not
    empty_first_file = 1
    # flag to indicate single or dual image
    single_image = False
    # flag to indicate whether or not we need to load intermediate images to get to our target
    multi_step_install = False

    # confirm image deletion
    del_system_image = False
    # confirm image deletion
    del_kickstart_image = True


def format_mac(syslog_mac=""):
    """
    Given mac address is formatted as XX:XX:XX:XX:XX:XX
    """
    syslog_mac = "%s:%s:%s:%s:%s:%s" % (
        syslog_mac[0:2], syslog_mac[2:4], syslog_mac[4:6],
        syslog_mac[6:8], syslog_mac[8:10],
        syslog_mac[10:12])
    return syslog_mac


def set_syslog_prefix():
    """
    Sets the appropriate POAP syslog prefix string based on
    POAP config mode.
    """
    global syslog_prefix
    if 'POAP_SERIAL' in os.environ:
        syslog_prefix = "S/N[%s]" % os.environ['POAP_SERIAL']
    if 'POAP_PHASE' in os.environ:
        if os.environ['POAP_PHASE'] == "USB":
            if 'POAP_RMAC' in os.environ:
                poap_syslog_mac = "%s" % os.environ['POAP_RMAC']
                syslog_prefix = "%s-MAC[%s]" % (
                    syslog_prefix, poap_syslog_mac)
                return
            if 'POAP_MGMT_MAC' in os.environ:
                poap_syslog_mac = "%s" % os.environ['POAP_MGMT_MAC']
                syslog_prefix = "%s-MAC[%s]" % (
                    syslog_prefix, poap_syslog_mac)
                return
        else:
            if 'POAP_MAC' in os.environ:
                poap_syslog_mac = "%s" % os.environ['POAP_MAC']
                poap_syslog_mac = format_mac(poap_syslog_mac)
                syslog_prefix = "%s-MAC[%s]" % (
                    syslog_prefix, poap_syslog_mac)
                return


def poap_cleanup_script_logs():
    """
    Deletes all the POAP log files in bootflash leaving
    recent 4 files.
    """
    file_list = sorted(glob.glob(os.path.join("/bootflash", '*poap*script.log')), reverse=True)
    poap_log("Found %d POAP script logs" % len(file_list))

    logs_for_removal = file_list[4:]
    for old_log in logs_for_removal:
        remove_file(old_log)


def poap_log(info):
    """
    Log the trace into console and poap_script log file in bootflash
    Args:
        file_hdl: poap_script log bootflash file handle
        info: The information that needs to be logged.
    """
    global log_hdl, syslog_prefix

    # Don't syslog passwords
    parts = re.split("\s+", info.strip())
    for (index, part) in enumerate(parts):
        # blank out the password after the password keyword (terminal password *****, etc.)
        if part == "password" and len(parts) >= index+2:
            parts[index+1] = "<removed>"

    # Recombine for syslogging
    info = " ".join(parts)

    # We could potentially get a traceback (and trigger this) before
    # we have called init_globals. Make sure we can still log successfully
    try:
        info = "%s - %s" % (syslog_prefix, info)
    except NameError:
        info = " - %s" % info

    syslog.syslog(9, info)
    if "log_hdl" in globals() and log_hdl is not None:
        log_hdl.write("\n")
        log_hdl.write(info)
        log_hdl.flush()


def remove_file(filename):
    """
    Removes a file if it exists and it's not a directory.
    """
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except (IOError, OSError) as e:
            poap_log("Failed to remove %s: %s" % (filename, str(e)))


def cleanup_file_from_option(option, bootflash_root=False):
    """
    Removes a file (indicated by the option in the POAP options) and removes it
    if it exists.

    We handle the cases where the variable is unused (defaults to None) or
    where the variable is not set yet (invoking this cleanup before we init)
    """
    if options.get(option) is not None:
        if bootflash_root:
            path = "/bootflash"
        else:
            path = options["destination_path"]

        remove_file(os.path.join(path, options[option]))
        remove_file(os.path.join(path, "%s.tmp" % options[option]))


def cleanup_files():
    """
    Cleanup all the POAP created files.
    """
    global options, log_hdl
    global del_system_image, del_kickstart_image

    poap_log("\n\nCleanup all files")

    # Destination config
    cleanup_file_from_option("destination_config")
    # Temporary split configs
    cleanup_file_from_option("split_config_first", True)
    cleanup_file_from_option("split_config_second", True)
    # Destination system or NXOS image
    if del_system_image is True:
        cleanup_file_from_option("destination_system_image")
    # Destination kickstart image
    if del_kickstart_image is True:
        cleanup_file_from_option("destination_kickstart_image")
    # Destination config
    cleanup_file_from_option("destination_config")
    os.system("rm -rf /bootflash/poap_files")
    os.system("rm -rf /bootflash_sup-remote/poap_files")
    os.system("rm -rf /bootflash/poap_replay01.cfg")

def sig_handler_no_exit(signum, stack):
    """
    A signal handler for the SIGTERM signal. Does not exit
    """
    poap_log("INFO: SIGTERM Handler while configuring boot variables")


def sigterm_handler(signum, stack):
    """
    A signal handler for the SIGTERM signal. Cleans up and exits
    """
    poap_log("INFO: SIGTERM Handler")
    if (len(options["install_path"]) != 0 and options["mode"] is not "personality"):
        abort("Cleaning up rpms")
    else:
        cleanup_files()
        log_hdl.close()
    exit(1)


def split_config_not_needed():
    """Checks if splitting the config into two config files is needed. This is needed on older
    images that require a reload to apply certain configs (e.g. TCAM changes). If we're on an
    image newer than or equal to 7.0(3)I4(1), we don't need reloads to apply configs.
    """
    global options

    """
    Device running in n3k mode still requires splitting of config.
    """
    if not 'START' in open('/tmp/first_setup.log').readline():
        poap_log("Split config is required, because box is not in N9K mode.")
        return False

    nxos_major = 0
    nxos_rev = 0

    # (nxos, 7, 0, 3, I4, 1, bin)
    # (n9000-dk9, 6, 1, 2, I1, 1, bin)

    parts = options['target_system_image'].split(".")
    
    # for latest images, it is (nxos, 9, minor, mr, bin)
    if int(parts[1]) >= 9:
        poap_log("Target image supports bootstrap replay. Split config is not required.")
        return True
    
    # number of parts should above 7 as above for us to check if its supported if not 9.x
    if len(parts) < 7:
        return False

    if parts[0] != "nxos":
        return False

    try:
        nxos_major = int(parts[1])
        if nxos_major < 7:
            return False
        elif nxos_major > 7:
            return True
    except ValueError:
        return False
    # NXOS 7x

    try:
        nxos_minor = int(parts[2])
        if nxos_minor > 0:
            return True
    except ValueError:
        return False
    # NXOS 7.0x

    try:
        nxos_rev = int(parts[3])
        if nxos_rev > 3:
            return True
        elif nxos_rev < 3:
            return False
    except ValueError:
        return False
    # NXOS 7.0.3.x

    if parts[4] >= "I4":
        return True
    # NXOS 7.0.3.I3 or less
    return False

def mtc_shut_member_ports(line, config_file_first):
    """
    In case bundling of any ports is done for mtc we shut down all the member
    ports. Apply speed 40000 followed by no shut on the first bundle port.
    Rest of the port configuration is handled as part of second config file.
    """
    global empty_first_file
    intf = map(int, re.findall('\d+', line))[0]
    port = map(int, re.findall('\d+', line))[1]
    if(port!=0):
        config_file_first.write('interface Ethernet' + str(intf) + '/' + str(port) + '\n')
        config_file_first.write("shut\n")
        config_file_first.write('interface Ethernet' + str(intf) + '/' + str(port+1) + '\n')
        config_file_first.write("shut\n")
        config_file_first.write('interface Ethernet' + str(intf) + '/' + str(port+2) + '\n')
        config_file_first.write("shut\n")
        config_file_first.write('interface Ethernet' + str(intf) + '/' + str(port+3) + '\n')
        config_file_first.write("shut\n")
        config_file_first.write('interface Ethernet' + str(intf) + '/' + str(port) + '\n')
        config_file_first.write("speed 40000\n")
        config_file_first.write("no shut\n")
        empty_first_file=0
        return 1
    else:
        return 0

def is_mtc():
    """
    Checks is the box is mtc or not using show module cli.
    MTC boxes are have mod id number as 3548
    """
    sh_mod_output = cli("show module")
    if(sh_mod_output.find("3548") != -1):
        return 1

def split_config_file():
    """
    Splits the downloaded switch configuration file into two files.
    File1: Contains lines of config that require switch reboot.
    File2: Contains lines of config that doesn't require switch reboot
    """
    poap_log("Split Config file")
    global empty_first_file, log_hdl, single_image, res_temp_flag, res_flag_dontprint
    res_temp_flag = 0
    res_flag_dontprint = 0
    skip_split_config = False

    config_file = open(os.path.join(options["destination_path"],
                                    options["destination_config"]), "r")
    config_file_first = open(os.path.join("/bootflash",
                                          options["split_config_first"]), "w+")
    config_file_second = open(os.path.join("/bootflash",
                                           options["split_config_second"]), "w+")

    # If we don't require extra reloads for commands (newer images), skip this
    # splitting of commands (and break the below loop immediately)
    if split_config_not_needed():
        config_file_second.write(config_file.read())
        line = ""
        poap_log("Skip split config as it isn't needed with %s" % options["target_system_image"])
    else:
        line = config_file.readline()

    while line != "":
        if (line.find("interface Ethernet") == 0):
            intf_eth_line=line
        if res_temp_flag == 1 and not skip_split_config:
            if line.find("arp-ether") != -1 \
               or line.find("copp") != -1\
               or line.find("e-ipv6-qos") != -1\
               or line.find("e-ipv6-racl") != -1\
               or line.find("e-mac-qos") != -1\
               or line.find("e-qos") != -1\
               or line.find("e-qos-lite") != -1\
               or line.find("e-racl") != -1\
               or line.find("fcoe-egress") != -1\
               or line.find("fcoe-ingress") != -1\
               or line.find("fex-ifacl") != -1\
               or line.find("fex-ipv6-ifacl") != -1\
               or line.find("fex-ipv6-qos") != -1\
               or line.find("fex-mac-ifacl") != -1\
               or line.find("fex-mac-qos") != -1\
               or line.find("fex-qos") != -1\
               or line.find("fex-qos-lite") != -1\
               or line.find("ifacl") != -1\
               or line.find("ipsg") != -1\
               or line.find("ipv6-ifacl") != -1\
               or line.find("ipv6-l3qos") != -1\
               or line.find("ipv6-qos") != -1\
               or line.find("ipv6-racl") != -1\
               or line.find("ipv6-vacl") != -1\
               or line.find("ipv6-vqos") != -1\
               or line.find("l3qos") != -1\
               or line.find("l3qos-lite") != -1\
               or line.find("mac-ifacl") != -1\
               or line.find("mac-l3qos") != -1\
               or line.find("mac-qos") != -1\
               or line.find("mac-vacl") != -1\
               or line.find("mac-vqos") != -1\
               or line.find("mcast-performance") != -1\
               or line.find("mcast_bidir") != -1\
               or line.find("mpls") != -1\
               or line.find("n9k-arp-acl") != -1\
               or line.find("nat") != -1\
               or line.find("ns-ipv6-l3qos") != -1\
               or line.find("ns-ipv6-qos") != -1\
               or line.find("ns-ipv6-vqos") != -1\
               or line.find("ns-l3qos") != -1\
               or line.find("ns-mac-l3qos") != -1\
               or line.find("ns-mac-qos") != -1\
               or line.find("ns-mac-vqos") != -1\
               or line.find("ns-qos") != -1\
               or line.find("ns-vqos") != -1\
               or line.find("openflow") != -1\
               or line.find("openflow-ipv6") != -1\
               or line.find("qos") != -1\
               or line.find("qos-lite") != -1\
               or line.find("racl") != -1\
               or line.find("redirect") != -1\
               or line.find("redirect-tunnel") != -1\
               or line.find("rp-ipv6-qos") != -1\
               or line.find("rp-mac-qos") != -1\
               or line.find("rp-qos") != -1\
               or line.find("rp-qos-lite") != -1\
               or line.find("sflow") != -1\
               or line.find("span") != -1\
               or line.find("span-sflow") != -1\
               or line.find("vacl") != -1 \
               or line.find("vpc-convergence") != -1 \
               or line.find("vqos") != -1 \
               or line.find("vqos-lite") != -1:
                config_file_first.write(line)
                res_flag_dontprint = 1
            else:
                res_temp_flag = 0
        if line.startswith("hardware profile tcam resource template"):
            res_temp_flag = 1
        if ((line.find("speed 40000") != -1) and is_mtc()):
            mtc_shut_member_ports(intf_eth_line, config_file_first)
            #Don't include speed in second config file.
            res_flag_dontprint = 1
        if res_temp_flag == 0 and line.startswith("system vlan") \
                or line.startswith("hardware profile portmode") \
                or line.startswith("hardware profile forwarding-mode warp") \
                or line.startswith("hardware profile forwarding-mode openflow-hybrid") \
                or line.startswith("hardware profile forwarding-mode openflow-only") \
                or line.startswith("hardware profile tcam") \
                or line.startswith("type fc") \
                or line.startswith("fabric-mode 40G") \
                or line.startswith("system urpf") \
                or line.startswith("no system urpf") \
                or line.startswith("hardware profile ipv6") \
                or line.startswith("system routing") \
                or line.startswith("hardware profile multicast service-reflect") \
                or line.startswith("ip service-reflect mode") \
                or line.startswith("udf") \
                or line.startswith("hardware profile unicast enable-host-ecmp"):
            config_file_first.write(line)
            if empty_first_file is 1:
                poap_log("setting empty file to 0 for line %s" % line)
                empty_first_file = 0
        elif res_flag_dontprint == 0:
            config_file_second.write(line)
        res_flag_dontprint = 0
        line = config_file.readline()

    # for poap across images set boot varible in the first config file
    poap_log("value of empty file is %d " % empty_first_file)
    if single_image is True:
        single_image_path = os.path.join(options["destination_path"],
                                         options["destination_system_image"])
        single_image_path = single_image_path.replace("/bootflash", "bootflash:", 1)
        if empty_first_file is 0:
            cmd = "boot nxos %s" % single_image_path
            poap_log("writing boot command: %s to first config file" % cmd)
            config_file_first.write("%s\n" % cmd)
        else:
            cmd = "boot nxos %s" % single_image_path
            poap_log("writing boot command: %s to second config file" % cmd)
            config_file_second.write("%s\n" % cmd)

    config_file.close()
    remove_file(os.path.join(options["destination_path"], options["destination_config"]))
    config_file_first.close()
    if empty_first_file is 1:
        remove_file(os.path.join(options["destination_path"], options["split_config_first"]))
    config_file_second.close()


def md5sum(filename):
    """
    Compute the md5 value for the file that is copied/downloaded.
    """
    if filename.startswith('/bootflash'):
        filename = filename.replace('/bootflash/', 'bootflash:', 1)

    poap_log("file name is %s" % filename)
    md5_sum = "Unknown"
    md5_output = cli("show file %s md5sum" % filename)
    if legacy:
        """
        Fetch the last entry from findall as some of the older nexus
        images had issues in fetching the value
        """
        result = re.findall(r'([a-fA-F\d]{32})', md5_output[1])
        if len(result) > 0:
            md5_sum = result[len(result) - 1]
    else:
        result = re.search(r'([a-fA-F\d]{32})', md5_output)
        if result is not None:
            md5_sum = result.group(1)

    poap_log("INFO: md5sum %s (recalculated)" % md5_sum)
    return md5_sum


def verify_md5(md5given, filename):
    """
    Verifies if the md5 value fetched from .md5 file matches with
    the md5 computed on the copied/downloaded file.
    Args:
        md5given: md5 value fetched from .md5 file
        filename: Name of the file that is copied/downloaded.
    """
    poap_log("Verifying MD5 checksum")
    if not os.path.exists("%s" % filename):
        poap_log("ERROR: File %s does not exit" % filename)
        return False

    md5calculated = md5sum(filename)

    try:
        file_size = os.path.getsize(filename)
    except OSError:
        poap_log("WARN: Failed to get size of %s" % filename)
        file_size = "Unknown"

    poap_log("Verifying MD5 checksum of %s (size %s)" % (filename, file_size))
    poap_log(" md5given = %s md5calculated = %s" % (
                 md5given, md5calculated))
    if md5given == md5calculated:
        poap_log("MD5 match for file = {0}".format(filename))
        return True
    poap_log("MD5 mis-match for file = {0}".format(filename))
    return False


def get_md5(filename, skip_abort = False):
    """
    Fetches the md5 value from .md5 file.
    Args:
        keyword: Keyword to look for in .md5 file
        filename: .md5 filename
    """
    # Get the MD5 file
    md5_filename = "%s.md5" % filename

    if not os.path.exists(os.path.join(options["destination_path"], md5_filename)):
        if (skip_abort is False):
            abort("MD5 file is missing (%s does not exist!)"
              % os.path.join(options["destination_path"], filename))
        else:
            raise
            
    file_hdl = open(os.path.join(options["destination_path"], md5_filename), "r")
    line = file_hdl.readline()
    while line != "":
        if line.find("md5sum", 0, len("md5sum")) != -1:
            line = line.split("=")[1].strip()
            file_hdl.close()
            return line
        if line.find(filename) != -1:
            line = re.split("\s+", line)[0]
            file_hdl.close()
            return line
        else:
            poap_log("Found non-MD5 checksum in %s: %s" % (md5_filename, line))
        line = file_hdl.readline()
    file_hdl.close()
    return ""

def get_bootflash_size():
    """
    Gets the bootflash size in KB from CLI.
    Output is handled differently for 6.x and 7.x or higher version.
    """
    cli_output = cli("show version")
    if legacy:
        result = re.search(r'bootflash:\s+(\d+)', cli_output[1])
        if result is not None:
            return int(result.group(1))
    else:
        result = re.search(r'bootflash:\s+(\d+)', cli_output)
        if result is not None:
            return int(result.group(1))
    poap_log("Unable to get bootflash size")


def do_copy(source="", dest="", login_timeout=10, dest_tmp="", compact=False, dont_abort=False):
    """
    Copies the file provided from source to destination. Source could
    be USB or external server. Appropriate copy function is required
    based on whether the switch runs 6.x or 7.x or higher image.
    """
    poap_log("Copying file options source=%s destination=%s "
             "login_timeout=%s destination_tmp=%s" % (source,
                                                      os.path.join(options["destination_path"],
                                                                   dest), login_timeout, dest_tmp))

    remove_file(os.path.join(options["destination_path"], dest_tmp))

    if os.environ.get("POAP_PHASE", None) == "USB":
        copy_src = os.path.join("/usbslot%s" % (options["usb_slot"]), source)

        dest_tmp = os.path.join(options["destination_path"], dest_tmp)
        if os.path.exists(copy_src):
            poap_log("%s exists" % source)
            poap_log("Copying from %s to %s" % (copy_src, dest_tmp))
            shutil.copy(copy_src, dest_tmp)
        else:
            abort("/usbslot%d/%s does NOT exist" % (options["usb_slot"], source))
    else:
        protocol = options["transfer_protocol"]
        host = options["hostname"]
        user = options["username"]
        password = options["password"]
        dest_tmp = os.path.join(options["destination_path"], dest_tmp)
        copy_tmp = dest_tmp.replace("/bootflash", "bootflash:", 1)
        vrf = options["vrf"]
        poap_log("Transfering using %s from %s to %s hostname %s vrf %s" % (
                 protocol, source, copy_tmp, host, vrf))
        if legacy:
            try:
                transfer(protocol, host, source, copy_tmp, vrf, login_timeout,
                         user, password)
                # The transfer module doesn't fail if bootflash runs out of space.
                # This is a bug with the already shipped transfer module, and there's
                # no return code or output that indicates this has happened. Newer
                # images have the "terminal password" CLI that lets us avoid this.
                poap_log("Copy done using transfer module. Please check size below")
            except Exception as e:
                # Handle known cases
                if "file not found" in str(e):
                    abort("Copy failed: %s" % str(e))
                elif "Permission denied" in str(e):
                    abort("Copy of %s failed: permission denied" % source)
                else:
                    raise
        else:
            # Add the destination path
            copy_cmd = "terminal dont-ask ; terminal password %s ; " % password
            if compact is True:
                if global_use_kstack is True:
                    copy_cmd += "copy %s://%s@%s%s %s compact vrf %s use-kstack" % (
                        protocol, user, host, source, copy_tmp, vrf)
                else:
                    copy_cmd += "copy %s://%s@%s%s %s compact vrf %s" % (
                        protocol, user, host, source, copy_tmp, vrf)
            elif (protocol is "https" and options["https_ignore_certificate"] is True):
                if global_use_kstack is True:
                    copy_cmd += "copy %s://%s@%s%s %s ignore-certificate vrf %s use-kstack" % (
                        protocol, user, host, source, copy_tmp, vrf)
                else:
                    copy_cmd += "copy %s://%s@%s%s %s ignore-certificate vrf %s" % (
                        protocol, user, host, source, copy_tmp, vrf)              
            else:
                if global_use_kstack is True:
                    copy_cmd += "copy %s://%s@%s%s %s vrf %s use-kstack" % (
                        protocol, user, host, source, copy_tmp, vrf)
                else:
                    copy_cmd += "copy %s://%s@%s%s %s vrf %s" % (
                        protocol, user, host, source, copy_tmp, vrf)
            poap_log("Command is : %s" % copy_cmd)
            try:
                cli(copy_cmd)
            except Exception as e:
                # scp compact can fail due to reasons of current image version or
                # platform do not support it; Try normal scp in such cases
                if compact is True and ("Syntax error while parsing" in str(e) or \
                     "Compaction is not supported on this platform" in str(e)):
                    return False
                # Remove extra junk in the message
                elif "no such file" in str(e):
                    if (dont_abort == True):
                        poap_log("Copy Failed. File/Directory not found")
                        pass
                    else:
                        abort("Copy of %s failed: no such file" % source)
                elif "Permission denied" in str(e):
                    abort("Copy of %s failed: permission denied" % source)
                elif "No space left on device" in str(e):
                    abort("Copy failed: No space left on device")
                else:
                    poap_log("Copy failed: %s" % str(e))
                    raise

    try:
        file_size = os.path.getsize(dest_tmp)
    except OSError:
        poap_log("WARN: Failed to get size of %s" % dest_tmp)
        file_size = "Unknown"

    poap_log("*** Downloaded file is of size %s ***" % file_size)

    dest = os.path.join(options["destination_path"], dest)

    try:
        os.rename(dest_tmp, dest)
    except KeyError as e:
        if (dont_abort == True): 
            return True
        else:
            abort("Failed to rename %s to %s: %s" % (dest_tmp, dest, str(e)))

    poap_log("Renamed %s to %s" % (dest_tmp, dest))
    return True


def create_destination_directories():
    """
    Creates the destination directory if it doesn't exist. For example, if the user
    specifies /bootflash/poap/files as the destination path, this function will create
    the directory "poap" and the directory "files" in the hierarchy above if they don't
    already exist.
    """
    try:
        os.makedirs(options["destination_path"])
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(options["destination_path"]):
            raise


def copy_md5_info(file_path, file_name):
    """
    Copies file with .md5 extension into bootflash

    Args:
        file_path: Directory where .md5 file resides
        file_name: Name of the .md5 file
    """
    poap_log("Copying MD5 information")

    md5_file_name = "%s.md5" % file_name
    if os.path.exists(os.path.join(options["destination_path"], md5_file_name)):
        remove_file(os.path.join(options["destination_path"], md5_file_name))

    tmp_file = "%s.tmp" % md5_file_name
    timeout = options["timeout_config"]
    src = os.path.join(file_path, md5_file_name)
    poap_log("Starting Copy of MD5. src = %s dest = %s" % (
                 src, os.path.join(options["destination_path"], md5_file_name)))
    if os.environ['POAP_PHASE'] != "USB":
        poap_log("File transfer_protocol = %s" % options["transfer_protocol"])
    
    if ("yaml" in src or "yml" in src):
        do_copy(src, md5_file_name, timeout, tmp_file, False, True)
        # True is passed as last parameter so that script does not abort on copy failure.
    else:
        do_copy(src, md5_file_name, timeout, tmp_file)


def copy_config():
    """
    Copies the configuration from the USB device or remote server to the switch
    If the mode is personality, the configuration is actually inside the tarball,
    so we skip copying any config from USB or the server at this point of execution
    """
    if options["mode"] != "personality":
        copy_remote_config()


def copy_remote_config():
    """
    Copies switch configuration file and verifies if the md5 of the config
    matches with the value present in .md5 file downloaded.
    """
    poap_log("Copying config file")
    global empty_first_file
    org_file = options["destination_config"]
    if options["disable_md5"] is False:
        copy_md5_info(options["config_path"], options["source_config_file"])
        md5_sum_given = get_md5(options["source_config_file"])
        remove_file(os.path.join(options["destination_path"], "%s.md5" %
                                 options["source_config_file"]))
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"], org_file)):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"], org_file)):
                poap_log("File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"], org_file))
                split_config_file()
                return
        elif not md5_sum_given:
            poap_log("MD5 sum given is invalid: %s" % md5_sum_given)
    poap_log("INFO: Starting Copy of Config File to %s" % os.path.join(options["destination_path"],
                                                                       org_file))
    tmp_file = "%s.tmp" % org_file
    timeout = options["timeout_config"]
    src = os.path.join(options["config_path"], options["source_config_file"])

    do_copy(src, org_file, timeout, tmp_file)

    if options["disable_md5"] is False:
        if md5_sum_given and not verify_md5(md5_sum_given,
                                            os.path.join(options["destination_path"], org_file)):
            abort("#### config file %s MD5 verification failed #####\n" % os.path.join(
                         options["destination_path"], org_file))
    split_config_file()
    poap_log("INFO: Completed copy of config file to %s" %
             os.path.join(options["destination_path"], org_file))

def is_image_cs_or_msll():
    
    if (os.path.exists("/isan/etc/cs.txt")):
        return 2
    
    if (os.path.exists("/isan/etc/noncs.txt")):
        return 1

    return 0
    
def target_system_image_is_currently_running():
    """
    Checks if the system image that we would try to download is the one that's
    currently running. Not used if MD5 checks are enabled.
    
    We need to check for both 64-bit as well as 32-bit, since from Jacksonville onwards, 
    both type of images are present. We have to check using this method, since we don't have
    a CLI to check whether the running image is a 64-bit image or a 32-bit image. 
    Image applicable from:  10.1(1) [Jacksonville]

    In case of mismatch between the currently running and target image, we check for the output from
    /isan/bin/pfm file, however exception may occur there (since this is an internal file, 
    subject to change)  so no need to check using it when doing comparison.  
    """
    version = get_version(1)
    if legacy is False:
        image_parts = [part for part in re.split("[\.()]", version) if part]
        image_parts.insert(0, "nxos")
        image_parts.append("bin")
        
        is_cs = is_image_cs_or_msll()
        image_parts64 = [part for part in re.split("[\.()]", version) if part]
       
        if is_cs == 2:
            image_parts64.insert(0, "nxos64-cs")
        elif is_cs == 1:
            image_parts64.insert(0, "nxos64-msll")
        else: 
            image_parts64.insert(0, "nxos64")
        
        image_parts64.append("bin")

        running_image = ".".join(image_parts)
        running_image64 = ".".join(image_parts64)
        
        global global_copy_image 
        if running_image == options["target_system_image"]:
            poap_log("Running: '%s'" % running_image)
            poap_log("Target:  '%s'" % options["target_system_image"])
            global_copy_image = False  
            return True
        elif running_image64 == options["target_system_image"]:
            poap_log("Running: '%s'" % running_image64)
            poap_log("Target: '%s'"  % options["target_system_image"])
            global_copy_image = False 
            return True
        else:
            if sp is not None:
                try: 
                    out = sp.check_output("file /isan/bin/pfm", stderr=sp.STDOUT, shell=True)
                    parts = out.strip().split()
                    is_32_bit = parts[2]
                    if (sys.version_info[0] >=3):
                        is_32_bit = is_32_bit.decode('utf-8')
                    if (is_32_bit == "64-bit"):
                         poap_log("Running 64-bit '%s' image" % running_image64)
                         poap_log("Target:  '%s'" % options["target_system_image"])
                    else:
                         poap_log("Running 32-bit '%s' image" % running_image)
                         poap_log("Target:  '%s'" % options["target_system_image"])
                except Exception as e: 
                     poap_log("Failed to find whether image is 32-bit or 64-bit.") 
            else:
                poap_log("As subprocess module is not present, unable to find if image is 32-bit or 64-bit.") 
            poap_log("Running image and target image are different. Need to copy target image to box.")
            return False

def copy_system():
    """
    Copies system/nxos image and verifies if the md5 of the image matches
    with the value present in .md5 file downloaded.
    """
    global del_system_image
    md5_sum_given = None
  
            
    if options["disable_md5"] is True and target_system_image_is_currently_running():
        poap_log("Currently running image is target image. Skipping system image download")
        return

    # do compact scp of system image if bootflash size is <= 2GB and "compact_image" option is enabled
    if options["compact_image"] is True and options["transfer_protocol"] is "scp":
        poap_log("INFO: Try image copy with compact option...")
        do_compact = True
    else:
        do_compact = False

    org_file = options["destination_system_image"]
    if options["disable_md5"] is False:
        copy_md5_info(options["target_image_path"], options["target_system_image"])
        md5_sum_given = get_md5(options["target_system_image"])
        remove_file(os.path.join(options["destination_path"], "%s.md5" %
                                 options["target_system_image"]))
        poap_log("MD5 for system image from server: %s" % md5_sum_given)
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"], options["target_system_image"])):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"], options["target_system_image"])):
                poap_log("File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"], options["target_system_image"]))
                """
                For multi-level install when the target system image is already
                present in the box, overwrite midway_system image name that is
                stored in destination_system_image with target_system_image.
                """
                options["destination_system_image"] = options["target_system_image"]
                del_system_image = False
                return
        elif not md5_sum_given:
            abort("Invalid MD5 from server: %s" % md5_sum_given)
        else:
            poap_log("File %s does not exist on switch" % options["target_system_image"])

    tmp_file = "%s.tmp" % org_file
    timeout = options["timeout_copy_system"]

    # For personality we use the personality path for everything
    src = os.path.join(options["target_image_path"], options["target_system_image"])

    poap_log("INFO: Starting Copy of System Image")

    ret = do_copy(src, org_file, timeout, tmp_file, do_compact)
    if do_compact is True and ret is False:
        poap_log("INFO: compact copy failed; Try normal copy...")
        do_compact = False
        do_copy(src, org_file, timeout, tmp_file)

    if options["disable_md5"] is False and md5_sum_given and do_compact is False:
        if not verify_md5(md5_sum_given,
                          os.path.join(options["destination_path"], org_file)):
            abort("#### System file %s MD5 verification failed #####\n" % os.path.join(
                         options["destination_path"], org_file))
    poap_log("INFO: Completed Copy of System Image to %s" % os.path.join(
        options["destination_path"], org_file))
    del_system_image = True


def copy_kickstart():
    """
    Copies kickstart image and verifies if the md5 of the image matches
    with the value present in .md5 file downloaded.
    """
    global del_kickstart_image
    poap_log("Copying kickstart image")
    org_file = options["destination_kickstart_image"]
    if options["disable_md5"] is False:
        copy_md5_info(options["target_image_path"], options["target_kickstart_image"])
        md5_sum_given = get_md5(options["target_kickstart_image"])
        remove_file(os.path.join(options["destination_path"], "%s.md5" %
                                 options["target_kickstart_image"]))
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"], options["target_kickstart_image"])):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"], options["target_kickstart_image"])):
                poap_log("INFO: File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"], options["target_kickstart_image"]))
                """
                For multi-level install when the target kickstart image is already
                present in the box, overwrite midway_kickstart image name that is
                stored in destination_kickstart_image with target_kickstart_image.
                """
                options["destination_kickstart_image"] = options["target_kickstart_image"]
                del_kickstart_image = False
                return

    tmp_file = "%s.tmp" % org_file
    timeout = options["timeout_copy_kickstart"]
    src = os.path.join(options["target_image_path"], options["target_kickstart_image"])
    do_copy(src, org_file, timeout, tmp_file)

    if options["disable_md5"] is False and md5_sum_given:
        if not verify_md5(md5_sum_given,
                          os.path.join(options["destination_path"], org_file)):
            abort("#### Kickstart file %s%s MD5 verification failed #####\n" % (
                         options["destination_path"], org_file))

    poap_log("INFO: Completed Copy of Kickstart Image to %s" % (
        os.path.join(options["destination_path"], org_file)))


def install_images_7_x():
    """
    Invoked when trying to install a 7.x or higher image. Boot variables are
    set appropriately and the startup config is updated.
    """
    poap_log("Checking if bios upgrade is needed")
    if is_bios_upgrade_needed():
        poap_log("Installing new BIOS (will take up to 5 minutes. Don't abort)")
        install_bios()

    poap_log("Installing NXOS image")

    system_image_path = os.path.join(options["destination_path"],
                                     options["destination_system_image"])
    system_image_path = system_image_path.replace("/bootflash", "bootflash:", 1)

    try:
        poap_log("config terminal ; boot nxos %s" % system_image_path)
        cli("config terminal ; boot nxos %s" % system_image_path)
    except Exception as e:
        poap_log("Failed to set NXOS boot variable to %s" % system_image_path)
        abort(str(e))

    command_successful = False
    timeout = 10  # minutes
    first_time = time.time()
    endtime = first_time + timeout * 60  # sec per min
    retry_delay = 30  # seconds
    while not command_successful:
        new_time = time.time()
        try:
            cli("copy running-config startup-config")
            command_successful = True
        except SyntaxError:
            poap_log("WARNING: copy run to start failed")
            if new_time > endtime:
                poap_log("ERROR: time out waiting for  \"copy run start\" to complete successfully")
                exit(-1)
            poap_log("WARNING: retry in 30 seconds")
            time.sleep(retry_delay)

    poap_log("INFO: Configuration successful")

def install_nxos_issu():
    ''' 
       global_copy_image is false implies that currently running and target_iamge
       have the same version. So, we do install all with the curretly booted image
       instead of doing it with the name specified in target_image, because actual
       copying of image may not have happened, leading to failure in ISSU if name of
       the target image is different from the image that the switch is currently booted
       up with. 
    ''' 
    if global_copy_image:
        system_image_path = os.path.join(options["destination_path"],
                                     options["destination_system_image"])
        system_image_path = system_image_path.replace("/bootflash", "bootflash:", 1)
    else:
        system_image_path = os.path.join("bootflash:",get_currently_booted_image_filename())
    
    try:
        os.system("touch /tmp/poap_issu_started")
        poap_log("terminal dont-ask ; install all nxos %s no-reload non-interruptive" % system_image_path)
        cli("terminal dont-ask ; install all nxos %s no-reload non-interruptive" % system_image_path)
        time.sleep(5)
        cli("terminal dont-ask ; write erase")
        time.sleep(5)
    except Exception as e:
        poap_log("Failed to ISSU to image %s" % system_image_path)
        os.system("rm -rf /tmp/poap_issu_started")
        abort(str(e))

# Procedure to install both kickstart and system images
def install_images():
    """
    Invoked when trying to install a 6.x based image. Bootvariables
    are set appropriately.

    If two step installation is true, just set the bootvariables and
    do no update startup-config so that step two of POAP is triggered.
    """
    kickstart_path = os.path.join(options["destination_path"],
                                  options["destination_kickstart_image"])
    kickstart_path = kickstart_path.replace("/bootflash", "bootflash:", 1)

    system_path = os.path.join(options["destination_path"],
                               options["destination_system_image"])
    system_path = system_path.replace("/bootflash", "bootflash:", 1)

    poap_log("Installing kickstart and system images")
    poap_log("######### Copying the boot variables ##########")
    cli("config terminal ; boot kickstart %s" % kickstart_path)
    cli("config terminal ; boot system %s" % system_path)

    command_successful = False
    timeout = 10  # minutes
    first_time = time.time()
    endtime = first_time + timeout * 60  # sec per min
    retry_delay = 30  # seconds
    while not command_successful:
        new_time = time.time()
        try:
            cli("copy running-config startup-config")
            command_successful = True
        except SyntaxError:
            poap_log("WARNING: copy run to start failed")
            if new_time > endtime:
                poap_log("ERROR: time out waiting for  \"copy run start\" to complete successfully")
                exit(-1)
            poap_log("WARNING: retry in 30 seconds")
            time.sleep(retry_delay)

    poap_log("INFO: Configuration successful")

    if multi_step_install is True:
        cli("config terminal ; terminal dont-ask ; write erase")
        poap_log("Midway image copy/setting done")
        exit(0)
    else:
        poap_log("Multi-level install not set, installed images")

#Procedure to intall using ISSU install command
def install_issu():
    ''' 
       global_copy_image is false implies that currently running and target_iamge
       have the same version. So, we do install all with the curretly booted image
       instead of doing it with the name specified in target_image, because actual
       copying of image may not have happened, leading to failure in ISSU if name of
       the target image is different from the image that the switch is currently booted
       up with. 
    '''
    if global_copy_image:
        system_image_path = os.path.join(options["destination_path"],
                                        options["destination_system_image"])
        system_image_path = system_image_path.replace("/bootflash", "bootflash:", 1)
    else:
        system_image_path = os.path.join("bootflash:",get_currently_booted_image_filename())
 
    img_upgrade_cmd = "config terminal ; terminal dont-ask"
    img_upgrade_cmd += " ; install all nxos %s non-interruptive override" % system_image_path
    try:
        output = cli(img_upgrade_cmd)
        file = open("/bootflash/install_output.txt","w")
        file.write(output)
        file.close()
    except Exception as e:
        s = os.statvfs("/bootflash/")
        freespace = (s.f_bavail * s.f_frsize)
        total_size = (s.f_blocks * s.f_frsize)
        percent_free = (float(freespace) / float(total_size)) * 100
        poap_log("%0.2f%% bootflash free" % percent_free)
        abort("Image install failed: %s" % str(e))
        
def parse_poap_yaml():
    """
    Parses the <serial_number>.yaml file and populates the dictionary
    """
    copy_path = options["install_path"] + "/" + options["serial_number"] + "/" + options["serial_number"] + ".yaml"
    alt_path = options["install_path"] + "/" + options["serial_number"] + "/" + options["serial_number"] + ".yml"
    timeout = options["timeout_copy_system"]
    dst = "poap_device_recipe.yaml"
    md5_sum_given = None
    md5_verification = True
    
    try:
        if options["disable_md5"] is False:
            copy_md5_info(os.path.join(options["install_path"], options["serial_number"]), options["serial_number"] + ".yaml")
            md5_sum_given = get_md5(options["serial_number"] + ".yaml")
            md5_verification = False
            do_copy(copy_path, dst, timeout, dst, False, False)
        else:
            do_copy(copy_path, dst, timeout, dst, False, True)
        # True is passed as last parameter so that script does not abort on copy failure.
        if options["disable_md5"] is False and md5_sum_given:
            md5_verification = verify_md5(md5_sum_given,
                      "/bootflash/poap_device_recipe.yaml")
            if not md5_verification:
                abort("#### Yaml file %s MD5 verification failed #####\n" % dst)
                time.sleep(2)
    except:
        try:
            if not md5_verification:
                exit(1)
            if options["disable_md5"] is False:
                copy_md5_info(os.path.join(options["install_path"], options["serial_number"]), options["serial_number"] + ".yml")
                md5_sum_given = get_md5(options["serial_number"] + ".yml")
                md5_verification = False
                do_copy(alt_path, dst, timeout, dst)
            else:
                do_copy(alt_path, dst, timeout, dst, False, True)
            if options["disable_md5"] is False and md5_sum_given:
                md5_verification = verify_md5(md5_sum_given,
                          "/bootflash/poap_device_recipe.yaml")
            if not md5_verification:
                    abort("#### Yaml file %s MD5 verification failed #####\n" % dst)
                    time.sleep(2)
        except:
            if md5_verification:
                poap_log("Although 'install_path' is set in poap script file, proceeding with legacy poap workflow because yaml file for device is not found")
                options["install_path"] = ""
                return
        if not md5_verification:
            exit(1)
    stream = open("/bootflash/poap_device_recipe.yaml", 'r')
    dictionary = yaml.load(stream)
    none_value_found = False
    for k in dictionary.keys():
        if dictionary[k] is None:
            none_value_found = True
            poap_log("Key {} has value None".format(k))
    if none_value_found:
        abort("Yaml has got keys with value None. Remove unwanted keys from yaml file.")
    if ("Version" not in dictionary):
        abort("Version keyword not found in yaml. Cannot proceed with installation.")
    elif ("Version" in dictionary and dictionary["Version"] is not 1):
        abort("Version given is not 1. Cannot be parsed for installation.")
    if ("Target_image" in dictionary):
        options["target_system_image"] = dictionary["Target_image"]
        options["destination_system_image"] = dictionary["Target_image"]
        
        
def validate_yaml_file():
    """
    Validates all the input filenames in the yaml file and throws error
    for wrong extension/rpm filename format.
    """
    stream = open("/bootflash/poap_device_recipe.yaml", 'r')
    dictionary = yaml.load(stream)
    wrong_files = []

    if ("License" in dictionary):
        for lic in dictionary["License"]:
             lic = lic.strip()
             if not lic.endswith('.lic'):
                 wrong_files += [lic]
    if ("RPM" in dictionary):
        for rpm in dictionary["RPM"]:
             rpm = rpm.strip()
             if not rpm.endswith('.rpm'):
                 wrong_files += [rpm]

    if ("Trustpoint" in dictionary):
        for ca in dictionary["Trustpoint"].keys():
            for cert, crypto_pass in dictionary["Trustpoint"][ca].items():
                cert = cert.strip()
                if not (cert.endswith('.pfx') or cert.endswith('.p12')):
                    wrong_files += [cert]

    if len(wrong_files) > 0:
        poap_log("Expected extensions are .lic for licenses, .rpm for RPM files and .pfx or .p12 for Trustpoint based certificates.")
        poap_log("The below files have wrong extension. Please rename in rpm source location and update YAML file accordingly.")
        for file in wrong_files:
            poap_log(file)
        abort()

        
def copy_poap_files():
    """
    Copies all the files as per the yaml file and places them in poap_files
    """
    stream = open("/bootflash/poap_device_recipe.yaml", 'r')
    dictionary = yaml.load(stream)
    os.system("mkdir -p /bootflash/poap_files")
    timeout = options["timeout_copy_system"]

    if ("License" in dictionary):
        for lic in dictionary["License"]:
            serial_path = os.path.join(options["install_path"], lic.strip())

            dst = "poap_files/" + lic.split('/')[-1]

            do_copy(serial_path, dst, timeout, dst, False)

    if ("RPM" in dictionary):
        rpm_error = False
        for rpm in dictionary["RPM"]:
            rpm = rpm.strip()
            serial_path = os.path.join(options["install_path"], rpm)

            dst = "poap_files/" + rpm.split('/')[-1]

            do_copy(serial_path, dst, timeout, dst, False)
        for rpm in dictionary["RPM"]:
            rpm = rpm.strip()
            name_str = "rpm -qp --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm' /bootflash/poap_files/"+ rpm.split('/')[-1]
            orig_name = subprocess.check_output(name_str, shell=True)
            orig_name = byte2str(orig_name)
            if (orig_name != rpm.split('/')[-1]):
                poap_log ("ERROR : RPM file %s does not match RPM package naming convention. Expected name: %s" %(rpm.split('/')[-1],orig_name))
                rpm_error = True
        if rpm_error:
            abort("Please correct the above rpm files in rpm source location and update YAML file accordingly.")
  
    if ("Certificate" in dictionary):
        for cert in dictionary["Certificate"]:
            cert  = cert.strip()
            serial_path = os.path.join(options["install_path"], cert)

            dst = "poap_files/" + cert.split('/')[-1]

            do_copy(serial_path, dst, timeout, dst, False)
    if ("Trustpoint" in dictionary):
        for ca in dictionary["Trustpoint"].keys():
            tmp_cmd = "mkdir -p /bootflash/poap_files/" + ca
            os.system(tmp_cmd)
            dst = "poap_files/" + ca + "/"
            for tp_cert, crypto_pass in dictionary["Trustpoint"][ca].items():
                tp_cert = tp_cert.strip()
                dst = dst + tp_cert.split('/')[-1]
                serial_path = os.path.join(options["install_path"], tp_cert)
                do_copy(serial_path, dst, timeout, dst, False)

   
def install_license():
    """
    Installs the license files.
    """

    conf_file_second = os.path.join("/bootflash", options["split_config_second"])
    tmp_file_second = conf_file_second + ".tmp"
    tmp_file_write = open(tmp_file_second, 'w')
    for file in os.listdir("/bootflash/poap_files"):
        if file.endswith(".lic"):
            poap_log("Installing license file: %s" % file)
            conf_file_second = os.path.join("/bootflash", options["split_config_second"])
            tmp_file_second = conf_file_second + ".tmp"

            tmp_file_write.write("install license bootflash:poap_files/%s\n" % file)
            poap_log("Installed license succesfully.")
    tmp_file_write.close()
    with open(conf_file_second, 'r') as read_file, open (tmp_file_second, 'a+') as write_file:
        write_file.write(read_file.read())
    os.rename(tmp_file_second, conf_file_second)

    poap_log("Installed all licenses succesfully.")

            
def check_if_rpm_in_file(file_name, rpm):
    """
    Check if any line in the file contains given rpm
    """
    if(not(os.path.exists(file_name))):
        return True
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            if rpm in line:
                return True
    return False


def install_rpm():
    """
    Installs the rpms for next reload
    """
    
    patch_count = 0
    activate_list = "committed_list = "
    version = get_version()
    image_parts = [part for part in re.split("[\.()]", version) if part]
    for file in os.listdir("/bootflash/poap_files"):
        if file.endswith(".rpm"):
            poap_log("Installing rpm file: %s" % file)
            os.system('echo "' + file + '" >> /bootflash/poap_files/success_install_list')
            group_string = "/usr/bin/rpm -qp --qf %{GROUP} /bootflash/poap_files/" + file
            rpm_string = "/usr/bin/rpm -qp --queryformat %{NXOSRPMTYPE} /bootflash/poap_files/" + file
            rpmgrp = subprocess.check_output(group_string, shell=True)
            rpmtype = subprocess.check_output(rpm_string, shell=True)
            if (len(rpmgrp) != 0 and 'Patch-RPM' in str(rpmgrp)):
                patch_rpm_name = file.replace(".rpm", "")
                if(not check_if_rpm_in_file("/bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf", patch_rpm_name)):
                    poap_log("RPM is a patch RPM. executing clis for the same.")
                    os.system("cp /bootflash/poap_files/%s /bootflash/.rpmstore/patching/patchrepo/" % file)
                    os.system("cp /bootflash/poap_files/%s /bootflash_sup-remote/.rpmstore/patching/patchrepo/" % file)
                    if(int(image_parts[0]) >= 10):
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/patching/patchrepo/")
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/patching/patchrepo/")
                    else:
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash/.rpmstore/patching/patchrepo/")
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py --update /bootflash_sup-remote/.rpmstore/patching/patchrepo/")
                    patch_count = patch_count + 1
                    activate_list  = activate_list + file.replace(".rpm", " ")
            else:
                if (len(rpmtype) != 0 and 'feature' in str(rpmtype)):
                    poap_log("RPM is a nxos RPM. executing clis for the same.")
                    os.system("cp /bootflash/poap_files/%s /bootflash/.rpmstore/patching/localrepo/" % file)
                    os.system("cp /bootflash/poap_files/%s /bootflash_sup-remote/.rpmstore/patching/localrepo/" % file)
                    if(int(image_parts[0]) >= 10):
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/patching/localrepo/")
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/patching/localrepo/")
                    else:                
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py /bootflash/.rpmstore/patching/localrepo/")
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py /bootflash_sup-remote/.rpmstore/patching/localrepo/")
                else:
                    poap_log("RPM is a third-party RPM. Executing clis for the same")
                    os.system("cp /bootflash/poap_files/%s /bootflash/.rpmstore/thirdparty/" % file)      
                    os.system("cp /bootflash/poap_files/%s /bootflash_sup-remote/.rpmstore/thirdparty/" % file)
                    if(int(image_parts[0]) >= 10):
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash/.rpmstore/thirdparty/")
                        os.system("sudo /usr/bin/createrepo_c --update /bootflash_sup-remote/.rpmstore/thirdparty/")      
                    else:
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py /bootflash/.rpmstore/thirdparty/")
                        os.system("sudo /usr/bin/python /usr/share/createrepo/genpkgmetadata.py /bootflash_sup-remote/.rpmstore/thirdparty/")
                rpm_name = subprocess.check_output("/usr/bin/rpm -qp --qf %%{NAME} /bootflash/poap_files/%s" %file, shell=True)
                rpm_name = byte2str(rpm_name)
                if not check_if_rpm_in_file("/bootflash/.rpmstore/nxos_rpms_persisted", rpm_name):
                    rpm_append_str = "/usr/bin/rpm -qp --qf %{NAME} /bootflash/poap_files/" + file + " >> /bootflash/.rpmstore/nxos_rpms_persisted"
                    os.system(rpm_append_str)
                    os.system('echo "" >> /bootflash/.rpmstore/nxos_rpms_persisted')
                    standby_append_str = "/usr/bin/rpm -qp --qf %{NAME} /bootflash/poap_files/" + file + " >> /bootflash_sup-remote/.rpmstore/nxos_rpms_persisted"
                    os.system(standby_append_str)
                    os.system('echo "" >> /bootflash_sup-remote/.rpmstore/nxos_rpms_persisted')
            poap_log("RPM %s scheduled to be installed on next reload. " % file)
    if (patch_count > 0):
        if((os.path.exists("/bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf"))):
            fp = open("/bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf", 'r')
            patching_meta = fp.readlines()
            patching_meta = ''.join(patching_meta)
            if("committed_list" in patching_meta):
                activate_list = activate_list.replace("committed_list = ", "")
                patch_append_str = 'sed -i "/committed_list/ s/$/ {0}/" /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf'.format(activate_list)
                standby_append_str = 'sed -i "/committed_list/ s/$/ {0}/" /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf'.format(activate_list)
                os.system(patch_append_str)
                os.system(standby_append_str)
            elif("[patching]" in patching_meta):
                patch_append_str = 'echo "' + activate_list + '" >> /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
                standby_append_str = 'echo "' + activate_list + '" >> /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
                os.system(patch_append_str)
                os.system(standby_append_str)
            else:
                os.system('echo "[patching]" >> /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf')
                os.system('echo "[patching]" >> /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf')
                patch_append_str = 'echo "' + activate_list + '" >> /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
                standby_append_str = 'echo "' + activate_list + '" >> /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
                os.system(patch_append_str)
                os.system(standby_append_str)
        else:
            os.system('echo "[patching]" >> /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf')
            os.system('echo "[patching]" >> /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf')
            patch_append_str = 'echo "' + activate_list + '" >> /bootflash/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
            standby_append_str = 'echo "' + activate_list + '" >> /bootflash_sup-remote/.rpmstore/patching/patchrepo/meta/patching_meta.inf'
            os.system(patch_append_str)
            os.system(standby_append_str)
        
def install_certificate():
    """
    Installs the certificate files.
    """
    stream = open("/bootflash/poap_device_recipe.yaml", 'r')
    dictionary = yaml.load(stream)
    config_file_second = open(os.path.join("/bootflash", options["split_config_second"]), "a+")
    
    if ("Trustpoint" in dictionary):
        for ca in dictionary["Trustpoint"].keys():
            ca_apply = 0
            for tp_cert, crypto_pass in dictionary["Trustpoint"][ca].items():
                tp_cert = tp_cert.strip()
                file = tp_cert.split('/')[-1]
                if (file.endswith(".p12") or file.endswith(".pfx")):
                    poap_log("Installing certificate file. %s" % file)
                    if (ca_apply == 0):
                        config_file_second.write("crypto ca trustpoint %s\n" % ca)
                        ca_apply = 1
                    config_file_second.write("crypto ca import %s pkcs12 bootflash:poap_files/%s/%s %s\n" % (ca, ca, file, crypto_pass))
                    poap_log("Installed certificate %s succesfully" % file)
            
            
def copy_standby_files():
    """
    Checks if the standby module is present and copies the
    poap_files folder to standby bootflash.
    """
    standby = cli("show module | grep ha-standby")
    if(len(standby) > 0):
        os.system("cp -rf /bootflash/poap_files /bootflash_sup-remote/")

                
def verify_freespace():
    """
    Checks if the available space in bootflash is sufficient enough to
    download config and required images.
    """
    poap_log("Verifying freespace in bootflash")
    s = os.statvfs("/bootflash/")
    freespace = (s.f_bavail * s.f_frsize) / 1024
    poap_log("Free bootflash space is %s" % freespace)

    if int(options["required_space"]) > freespace:
        abort("*** Not enough bootflash space to continue POAP ***")


def set_cfg_file_serial():
    """
    Sets the name of the switch config file to download based on chassis
    serial number. e.g conf_FOC3825R1ML.cfg
    """
    poap_log("Setting source cfg filename based-on serial number")

    if 'POAP_SERIAL' in os.environ:
        poap_log("serial number %s" % os.environ['POAP_SERIAL'])
        options["source_config_file"] = "conf.%s" % os.environ['POAP_SERIAL']
        options["serial_number"] = os.environ['POAP_SERIAL']
    poap_log("Selected conf file name : %s" % options["source_config_file"])


def set_cfg_file_mac():
    """
    Sets the name of the switch config file to download based on interface
    MAC address. e.g conf_7426CC5C9180.cfg
    """
    poap_log("Setting source cfg filename based on the interface MAC")
    if os.environ.get("POAP_PHASE", None) == "USB":
        if options["usb_slot"] is 2:
            poap_log("usb slot is 2")

        config_file = "conf_%s.cfg" % os.environ['POAP_RMAC']
        options["serial_number"] = os.environ['POAP_RMAC']
        poap_log("Router MAC conf file name : %s" % config_file)
        if os.path.exists("/usbslot%d/%s" % (usbslot, config_file)):
            options["source_config_file"] = config_file
            poap_log("Selected conf file name : %s" % options["source_config_file"])
            return
        config_file = "conf_%s.cfg" % os.environ['POAP_MGMT_MAC']
        options["serial_number"] = os.environ['POAP_MGMT_MAC']
        poap_log("MGMT MAC conf file name : %s" % config_file)
        if os.path.exists("/usbslot%d/%s" % (options["usb_slot"], config_file)):
            options["source_config_file"] = config_file
            poap_log("Selected conf file name : %s" % options["source_config_file"])
            return
    else:
        if 'POAP_MAC' in os.environ:
            poap_log("Interface MAC %s" % os.environ['POAP_MAC'])
            options["source_config_file"] = "conf_%s.cfg" % os.environ['POAP_MAC']
            options["serial_number"] = os.environ['POAP_MAC']
            poap_log("Selected conf file name : %s" % options["source_config_file"])


def set_cfg_file_host():
    """
    Sets the name of the switch config file to download based on hostname
    received in the DHCP option. e.g conf_TestingSw.cfg
    """
    poap_log("Setting source cfg filename based on switch hostname")
    if 'POAP_HOST_NAME' in os.environ:
        poap_log("Host Name: [%s]" % os.environ['POAP_HOST_NAME'])
        options["source_config_file"] = "conf_%s.cfg" % os.environ['POAP_HOST_NAME']
    else:
        poap_log("Host Name information missing, falling back to static mode")
    poap_log("Selected conf file name : %s" % options["source_config_file"])


def set_cfg_file_location():
    """
    Sets the name of the switch config file to download based on cdp
    information. e.g conf_switch_Eth1_32.cfg
    """
    poap_log("Setting source cfg filename")
    poap_log("show cdp neighbors interface %s" % os.environ['POAP_INTF'])
    cdp_output = cli("show cdp neighbors interface %s" % os.environ['POAP_INTF'])

    if legacy:
        cdp_lines = cdp_output[1].split("\n")
    else:
        cdp_lines = cdp_output.split("\n")

    if len(cdp_lines) == 0:
        abort("No CDP neighbor output for %s" % os.environ['POAP_INTF'])

    if re.match("\s*Note:", cdp_lines[0]):
        abort("No CDP neighbors found for %s" % os.environ['POAP_INTF'])

    i = 0
    while i < len(cdp_lines):
        if cdp_lines[i].startswith("Device-ID"):
            break
        i += 1
    else:
        abort("Improper CDP output (missing heading): %s" % "\n".join(cdp_lines))
    i += 1

    cdp_info = [info for info in re.split("\s+", " ".join(cdp_lines[i:])) if info != ""]

    switch_name_tuple = cdp_info[0].split("(")

    # Split the serial number if it exists. Sometimes the serial number doesn't exist so
    # just take the hostname as it is
    if len(switch_name_tuple) in [1, 2]:
        switch_name = switch_name_tuple[0]
    else:
        abort("Improper CDP output (name and serial number malformed): %s" % "\n".join(cdp_lines))

    i = 0
    while i < len(cdp_info):
        # 7x code prints out total entries
        if cdp_info[i] == "Total":
            intf_name = cdp_info[i-1]
            break
        i += 1
    else:
        # 3K 6x and older releases don't print this info
        intf_name = cdp_info[-1]

    options["source_config_file"] = "conf_%s_%s.cfg" % (switch_name, intf_name)
    options["source_config_file"] = options["source_config_file"].replace("/", "_")
    poap_log("Selected conf file name : %s" % options["source_config_file"])


def get_version(option=0):
    """
    Gets the image version of the switch from CLI.
    Output is handled differently for 6.x and 7.x or higher version.
    """
    is_Feature_Release = False 
    final_version = ""

    cli_output = cli("show version")
    if legacy:
        result = re.search(r'system.*version\s*(.*)\n', cli_output[1])
        if result is not None:
            return result.group(1)
    else:
        result = re.search(r'NXOS.*version\s*(.*)\n', cli_output)
        #Line is of type NXOS: version <version>
        if result is not None and option != 1:
           return result.group(1)
        elif result is not None:   
           #This checks if the image if of intermediate type of CCO
           #If 'build' is present, then it is of intermediate type
            interim_result = result.group()
            if 'Feature Release' in interim_result:
                is_Feature_Release = True 
          
            if 'build' in interim_result:
                # We are extracting our answer from the interim_result extracted so far
                # Whatever we were extracting till now isn't enough
                # This is an intermediate image, so our interim result is of form: nxos.9.4.1. [build 10.1.0.60.].bin
                final_version = re.search(r'build.*', interim_result)
                final_version = final_version.group()
                final_version = final_version.replace('(', '.').replace(')', '.').replace(']', '').split()[1]
                 
                # Now, the form obtained if of the form 10.1.0.60, and it is a string. 
                #return final_version        
            else:
                #This fetches the CCO image version
                # interim_result is of form major.minor (patch version)
                final_version = interim_result.replace('(', '.').replace(')', '')
                final_version = final_version.split()[2]
                #return final_version
    
    if final_version == "":
        poap_log("Unable to get switch version")
    if is_Feature_Release:
        final_version  = final_version + ".F"
    
    return final_version 

def get_bios_version():
    """
    Gets the BIOS version of the switch from CLI.
    Output is handled differently for 6.x and 7.x/higher version.
    """
    cli_output = cli("show version")
    if legacy:
        result = re.search(r'BIOS.*version\s*(.*)\n', cli_output[1])
        if result is not None:
            return result.group(1)
    else:
        result = re.search(r'BIOS.*version\s*(.*)\n', cli_output)
        if result is not None:
            return result.group(1)
    poap_log("Unable to get switch Bios version")


def install_bios():
    """
    Upgrade the bios when moving from 6.X to 7.X
    """
    single_image_path = os.path.join(options["destination_path"],
                                     options["destination_system_image"])
    single_image_path = single_image_path.replace("/bootflash", "bootflash:", 1)

    bios_upgrade_cmd = "config terminal ; terminal dont-ask"
    bios_upgrade_cmd += " ; install all nxos %s bios" % single_image_path
    try:
        cli(bios_upgrade_cmd)
    except Exception as e:
        s = os.statvfs("/bootflash/")
        freespace = (s.f_bavail * s.f_frsize)
        total_size = (s.f_blocks * s.f_frsize)
        percent_free = (float(freespace) / float(total_size)) * 100
        poap_log("%0.2f%% bootflash free" % percent_free)
        abort("Bios install failed: %s" % str(e))

    poap_log("Bios successfully upgraded to version %s" % get_bios_version())


def is_bios_upgrade_needed():
    """
    Check if bios upgrade is required. It's required when the current
    bios is not 3.x and image upgrade is from 6.x to 7.x or higher
    """
    global single_image
    last_upgrade_bios = 3
    ver = get_version()
    bios = get_bios_version()
    poap_log("Switch is running version %s with bios version %s"
             " image %s single_image %d" % (ver, bios, options["target_system_image"],
                                            single_image))
    if re.match("nxos.", options["target_system_image"]):
        poap_log("Upgrading to a nxos image")
        try:
            bios_number = float(bios)
        except ValueError:
            major, minor = bios.split(".", 1)
            try:
                bios_number = int(major)
            except ValueError:
                poap_log("Could not convert BIOS '%s' to a number, using text match")
                bios_number = bios
        try:
            chassis_out = cli("show chassis-family")
            chassis = chassis_out.split()
            if chassis[-1] == 'Fretta':
                last_upgrade_bios = 1
        except:
            poap_log("Could not find chassis family.")
        
        poap_log("Comparing present BIOS version %d with base version %d" % (bios_number, last_upgrade_bios))
        if bios_number < last_upgrade_bios:
            poap_log("Bios needs to be upgraded as switch is "
                     "running older bios version")
            return True
    poap_log("Bios upgrade not needed")
    return False


def find_upgrade_index_from_match(image_info):
    """
    Given the current image match (in the form of a re match object), we
    extract the version information and see where on the upgrade path it lies.
    The returned index will indicate which upgrade is the next one.

    The recommended upgrade path for N3K is below:
        * older than 5.0(3)U5(1)
        * 5.0(3)U5(1)
        * 6.0(2)U6(2a)
        * 6.0(2)U6(7)
        * newer than 6.0(2)U6(7)

    N9K images have always been greater revisions than anything in this path so this
    method will return len(upgrade_path) on N9K
    """
    upgrade_path = [('5', '0', '3', '5', '1'), ('6', '0', '2', '6', '2a'),
                    ('6', '0', '2', '6', '7')]

    major = image_info.group(1)
    minor = image_info.group(2)
    revision = image_info.group(3)
    #Ignore the branch and release details for 9.2 or higher versions
    if int(major) < 9:
       branch = image_info.group(4)
       release = image_info.group(5)
    else:
       branch=0
       release=0

    i = 0

    while i < len(upgrade_path):
        # Major
        if major < upgrade_path[i][0]:
            return i
        elif major > upgrade_path[i][0]:
            i += 1
        # Minor
        elif minor < upgrade_path[i][1]:
            return i
        elif minor > upgrade_path[i][1]:
            i += 1
        # Revision
        elif revision < upgrade_path[i][2]:
            return i
        elif  revision > upgrade_path[i][2]:
            i += 1
        # Branch
        elif branch < upgrade_path[i][3]:
            return i
        elif branch > upgrade_path[i][3]:
            i += 1
        # Release
        elif release < upgrade_path[i][4]:
            return i
        elif release > upgrade_path[i][4]:
            i += 1
        else:
            #Exact match, return next index
            return i + 1
    return i


def get_currently_booted_image_filename():
    match = None
    if legacy:
        try:
            output = cli("show version")[1]
        except Exception as e:
            abort("Show version failed: %s" % str(e))

        match = re.search("system image file is:\s+(.+)", output)
    else:
        try:
            output = cli("show version")
        except Exception as e:
            abort("Show version failed: %s" % str(e))

        match = re.search("NXOS image file is:\s+(.+)", output)

    if match:
        directory, image = os.path.split(match.group(1))
        return image.strip()
    return ""


def set_next_upgrade_from_user():
    """
    Forces a 2 step upgrade if initiated by the user. We first check if we're currently on the
    midway image, and if not, we make that the next image we're going to boot into.
    """
    global multi_step_install

    current_image_file = get_currently_booted_image_filename()

    # The currently booted image file is not the midway destination file. That means
    # that we did not already do the midway step, and we need to go there next
    if options["destination_midway_system_image"] != current_image_file:
        poap_log("Destination midway image %s is not currently booted (%s)" %
                 (options["destination_midway_system_image"], current_image_file))

        options["target_kickstart_image"] = options["midway_kickstart_image"]
        options["target_system_image"] = options["midway_system_image"]

        version = get_version()
        poap_log("Next upgrade is to %s from %s (forced by user)" %
                 (options["midway_system_image"], version))

        # Keep overwriting midway images
        options["destination_kickstart_image"] = options["destination_midway_kickstart_image"]
        options["destination_system_image"] = options["destination_midway_system_image"]
        multi_step_install = True
    else:
        poap_log("Already on the midway image, upgrading to %s next." %
                 options["target_system_image"])


def set_next_upgrade_from_upgrade_path():
    """Checks the currently running image and the target image to see where on the upgrade path
    the images lie. If there's a recommended upgrade between the current image and the target image
    then that recommended upgrade is used as a midway image to jump between the current image
    and the target. Setting the "midway_system_image" and "midway_kickstart_image" options will
    override the upgrade that is used if we detect that we need to follow the upgrade path.
    """
    global options
    global multi_step_install

    # 5.0(3)U5(1), 6.0(2)U6(2a), 6.0(2)U6(7), 7.0(3)I3(1)
    upgrade_images = [["n3000-uk9-kickstart.5.0.3.U5.1.bin", "n3000-uk9.5.0.3.U5.1.bin"],
                      ["n3000-uk9-kickstart.6.0.2.U6.2a.bin", "n3000-uk9.6.0.2.U6.2a.bin"],
                      ["n3000-uk9-kickstart.6.0.2.U6.7.bin", "n3000-uk9.6.0.2.U6.7.bin"]]

    # Check currently running image
    version = get_version()

    image_info = re.match("(\d+)\.(\d+)\((\d+)\)[A-Z]+(\d+)\((\w+)\)", version)
    if image_info is None:
        #try the regex match for 9.2(1) or higher version scheme
        image_info = re.match("(\d+)\.(\d+)\((\d+)[a-z]?\)", version)
        if image_info is None:
            abort("Failed to extract image information from %s" % version)

    current_idx = find_upgrade_index_from_match(image_info)

    # Check the target image
    image_info = re.search("[\w-]+\.(\d+)\.(\d+)\.(\d+)\.[A-Z]+(\d+)\.(\w+)",
                           options["target_system_image"])

    if image_info is None:
        #try the regex match for 9.2 or higher version scheme
        image_info = re.search("[\w-]+\.(\d+)\.(\d+)\.(\d+)", options["target_system_image"])
        if image_info is None:
            poap_log("Failed to match target image: %s" % options["target_system_image"])
            exit(1)

    target_idx = find_upgrade_index_from_match(image_info)

    if (target_idx - current_idx) > 0:
        poap_log("Multi-level install is set")

        # Update the target image with the upgrade path midway images
        options["target_kickstart_image"] = upgrade_images[current_idx][0]
        options["target_system_image"] = upgrade_images[current_idx][1]

        poap_log("Next upgrade is %s from %s" % (str(upgrade_images[current_idx][1]), version))

        # Keep overwriting midway images
        options["destination_kickstart_image"] = options["destination_midway_kickstart_image"]
        options["destination_system_image"] = options["destination_midway_system_image"]

        multi_step_install = True
    else:
        poap_log("Multi-level install is not needed")


def download_personality_tarball():
    """
    Downloads the personality tarball and verifies if the md5 of the tar
    matches with the value .md5 file downloaded.
    """
    md5_sum_given = None
    if options["disable_md5"] is False:
        copy_md5_info(options["personality_path"], options["destination_tarball"])
        md5_sum_given = get_md5(options["destination_tarball"])
        remove_file(os.path.join(options["destination_path"], "%s.md5" %
                                 options["destination_tarball"]))
        poap_log("MD5 for tar from server: %s" % md5_sum_given)
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"],
                                            options["destination_tarball"])):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"],
                                                      options["destination_tarball"])):
                poap_log("File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"],
                                      options["destination_tarball"]))
                return
        elif not md5_sum_given:
            abort("Invalid MD5 from server: %s" % md5_sum_given)
        else:
            poap_log("File %s does not exist on switch" %
                     options["destination_tarball"])

    tarball_path = os.path.join(options["personality_path"], options["source_tarball"])
    tmp_file = "%s.tmp" % options["destination_tarball"]
    do_copy(tarball_path, options["destination_tarball"],
            options["timeout_copy_personality"], tmp_file)

    if options["disable_md5"] is False and md5_sum_given:
        if not verify_md5(md5_sum_given, os.path.join(options["destination_path"],
                                                      options["destination_tarball"])):
            abort("#### Tar file %s MD5 verification failed #####\n" %
                  os.path.join(options["destination_path"],
                               options["destination_tarball"]))
    poap_log("INFO: Completed Copy of Tar file to %s" %
             os.path.join(options["destination_path"],
                          options["destination_tarball"]))


def get_system_image_from_tarball():
    """
    Extracts the system image name from the tarball
    """
    global options

    tarball_path = os.path.join(options["destination_path"], options["destination_tarball"])

    tar = tarfile.open(tarball_path)

    file_list = tar.getnames()
    for file_name in file_list:
        # Legacy personality support
        match = re.search("IMAGEFILE_(.+)", file_name)
        if match:
            options["target_system_image"] = byte2str(match.group(1))
        # File container way
        elif os.path.basename(file_name) == "IMAGEFILE":
            options["target_system_image"] = byte2str(tar.extractfile(file_name).read().strip())

    if options.get("target_system_image") is None:
        abort("Failed to find system image filename from tarball")

    poap_log("Using %s as the system image" % options["target_system_image"])


def override_options_for_personality():
    """
    Overrides the existing options with the personality specific ones
    """
    global options

    options["target_image_path"] = options["personality_path"]
    poap_log("target_image_path option set to personality_path (%s)" % options["personality_path"])
    options["destination_system_image"] = options["target_system_image"]


def initialize_personality():
    """
    Initializes personality. Downloads the tarball and extracts the system image
    """
    download_personality_tarball()
    get_system_image_from_tarball()
    override_options_for_personality()


def setup_mode():
    """
    Sets the config file name based on the mode
    """
    supported_modes = ["location", "serial_number", "mac", "hostname",
                       "personality", "raw"]
    if options["mode"] == "location":
        set_cfg_file_location()
        options["serial_number"] = os.environ['POAP_SERIAL']
    elif options["mode"] == "serial_number":
        set_cfg_file_serial()
    elif options["mode"] == "mac":
        set_cfg_file_mac()
    elif options["mode"] == "hostname":
        set_cfg_file_host()
        options["serial_number"] = os.environ['POAP_SERIAL']
    elif options["mode"] == "personality":
        initialize_personality()
    elif options["mode"] == "raw":
        # Don't need to change the name of the config file
        options["serial_number"] = os.environ['POAP_SERIAL']
        pass
    else:
        poap_log("Invalid mode selected: %s" % options["mode"])
        poap_log("Mode must be one of the following: %s" % ", ".join(supported_modes))
        abort()


def setup_logging():
    """
    Configures the log file this script uses
    """
    global log_hdl

    if os.environ.get("POAP_PHASE", None) == "USB":
        poap_script_log = "/bootflash/%s_poap_%s_usb_script.log" % (
                                                              strftime("%Y%m%d%H%M%S", gmtime()),
                                                              os.environ['POAP_PID'])
    else:
        poap_script_log = "/bootflash/%s_poap_%s_script.log" % (strftime("%Y%m%d%H%M%S", gmtime()),
                                                                os.environ['POAP_PID'])
    log_hdl = open(poap_script_log, "w+")

    poap_log("Logfile name: %s" % poap_script_log)

    poap_cleanup_script_logs()


def check_multilevel_install():
    """
    Checks whether or not the multi-level install procedure is needed. Sets
    multi_step_install to True if it is needed. Also sets single_image to
    True if the target image is a 7x or higher image.
    """
    global options, single_image
    
    # User wants to override multi level install
    if options["skip_multi_level"] == True:
        single_image = True
        return

    # User wants to override multi level install
    if options["skip_multi_level"] == True:
        single_image = True
        return

    # User wants to override the midway image
    if options["midway_system_image"] != "":
        set_next_upgrade_from_user()
    else:
        if re.match("nxos.", options["target_system_image"]) \
            or re.match("n9000", options["target_system_image"]):
            poap_log("Single image is set")
            single_image = True
        else:
            poap_log("Single image is not set")
            single_image = False
            set_next_upgrade_from_upgrade_path()

def invoke_personality_restore():
    """
    Does a write erase (so POAP will run again) and invokes the
    POAP Personality restore CLI.
    """
    cli("terminal dont-ask ; write erase")

    try:
        cli("personality restore %s user-name %s password %s hostname %s vrf %s" % (
            options["destination_tarball"], options["username"], options["password"],
            options["hostname"], options["vrf"]))
    except Exception as e:
        # If this fails, personality will have already thrown an error
        abort("Personality has failed! (%s)" % str(e))


def cleanup_temp_images():
    """
    Cleans up the temporary images if they exist. These are the midway images
    that are downloaded for multi-level install
    """
    if options["destination_kickstart_image"] != options["destination_midway_kickstart_image"]:
        midway_kickstart = os.path.join(options["destination_path"],
                                        options["destination_midway_kickstart_image"])
        remove_file(midway_kickstart)
    if options["destination_system_image"] != options["destination_midway_system_image"]:
        midway_system = os.path.join(options["destination_path"],
                                     options["destination_midway_system_image"])
        remove_file(midway_system)


def main():
    signal.signal(signal.SIGTERM, sigterm_handler)

    # Set all the default parameters and validate the ones provided
    set_defaults_and_validate_options()

    # Configure the logging for the POAP process
    setup_logging()

    # Initialize parameters based on the mode
    setup_mode()

    # Set the prefix for syslogs based on the POAP mode
    set_syslog_prefix()

    # Verify there's enough space (and fail if not)
    verify_freespace()

    # Now that we know we're going to try and copy, let's create
    # the directory structure needed, if any
    create_destination_directories()

    if (len(options["install_path"]) != 0 and options["mode"] is not "personality"):
        parse_poap_yaml()
    check_multilevel_install()
    # In two step install we just copy the midway image and reboot.
    # Config copy and script download happens in the second step.
    if multi_step_install is False:
        copy_config()

        # Download user scripts and agents
        download_scripts_and_agents()
        # End of multi_step_install is False block

    if (len(options["install_path"]) != 0 and options["mode"] is not "personality"):
        validate_yaml_file()
        copy_poap_files()
        time.sleep(2)
        install_license()
        install_rpm()
        time.sleep(2)
        install_certificate()
        time.sleep(2)
        copy_standby_files()
        
    copy_system()

    if single_image is False:
        copy_kickstart()

    signal.signal(signal.SIGTERM, sig_handler_no_exit)
    # install images
    if single_image is False:
        install_images()
    elif global_upgrade_bios:
        install_issu()
    elif options["use_nxos_boot"]:
        install_images_7_x()

    # Cleanup midway images if any
    cleanup_temp_images()

    # Invoke personality restore if personality is enabled
    if options["mode"] == "personality":
        invoke_personality_restore()
        exit(0)

    if empty_first_file is 0:
        cli('copy bootflash:%s scheduled-config' % options["split_config_first"])
        poap_log("Done copying the first scheduled cfg")
        remove_file("/bootflash/%s" % options["split_config_first"])

    cli('copy bootflash:%s scheduled-config' % options["split_config_second"])
    poap_log("Done copying the second scheduled cfg")
    remove_file(os.path.join("/bootflash", options["split_config_second"]))
    if (options["use_nxos_boot"] is False):
        install_nxos_issu()

    log_hdl.close()
    exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        poap_log("Exception: {0} {1}".format(exc_type, exc_value))
        while exc_tb is not None:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            poap_log("Stack - File: {0} Line: {1}"
                     .format(fname, exc_tb.tb_lineno))
            exc_tb = exc_tb.tb_next
        abort()

