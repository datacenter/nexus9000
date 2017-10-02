#!/bin/env python
#md5sum="a39fc249d01b49ddee8c119275eaace7"
"""
If any changes are made to this script, please run the below command
in bash shell to update the above md5sum. This is used for an integrity check.
f=poap.py ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i \
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
# Host name and user credentials
options = {
   "username": "root",
   "password": "password",
   "hostname": "2.1.1.1",
   "transfer_protocol": "scp",
   "mode": "hostname",
   "target_system_image": "nxos.7.0.3.I4.4.bin",
}


def download_scripts_and_agents():
    """
    Downloads user scripts, agents, and data after installing the target image, but before reload
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
    missing_parameters = required_parameters.difference(options.keys())
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
    set_default("config_path", "/")
    # Target image and its path (single image is default)
    set_default("target_system_image", "")
    set_default("target_image_path", "/")
    set_default("target_kickstart_image", "")
    # Destination image and its path
    set_default("destination_path", "/bootflash/")
    set_default("destination_system_image", options["target_system_image"])
    set_default("destination_kickstart_image", options["target_kickstart_image"])
    set_default("destination_midway_system_image", "midway_system.bin")
    set_default("destination_midway_kickstart_image", "midway_kickstart.bin")

    # User app path
    set_default("user_app_path", "/")

    # MD5 Verification
    set_default("disable_md5", False)

    # Midway system and kickstart source file name.
    # This should be a 6.x U6 or greater dual image.
    # Required only if moving from pre 6.x U6 image to 7.x image.
    set_default("midway_system_image", "")
    set_default("midway_kickstart_image", "")
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

    # Check that options are valid
    validate_options()


def validate_options():
    """
    Validates that the options provided by the user are valid.
    Aborts the script if they are not.
    """
    if os.environ.get("POAP_PHASE", None) == "USB" and options["mode"] == "personality":
        abort("POAP Personality is not supported via USB!")

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


def abort(msg=None):
    """
    Aborts the POAP script execution with an optional message.
    """
    global log_hdl

    if msg is not None:
        poap_log(msg)

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
    del_system_image = True
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

    poap_log("Cleanup all files")

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
    cleanup_files()
    log_hdl.close()
    exit(1)


def split_config_not_needed():
    """Checks if splitting the config into two config files is needed. This is needed on older
    images that require a reload to apply certain configs (e.g. TCAM changes). If we're on an
    image newer than or equal to 7.0(3)I4(1), we don't need reloads to apply configs
    """
    global options
    nxos_major = 0
    nxos_rev = 0

    # (nxos, 7, 0, 3, I4, 1, bin)
    # (n9000-dk9, 6, 1, 2, I1, 1, bin)

    parts = options['target_system_image'].split(".")
    # number of parts should above 7 as above for us to check if its supported
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
        if res_temp_flag == 0 and line.startswith("system vlan") \
                or line.startswith("hardware profile portmode") \
                or line.startswith("hardware profile forwarding-mode warp") \
                or line.startswith("hardware profile tcam") \
                or line.startswith("type fc") \
                or line.startswith("fabric-mode 40G") \
                or line.startswith("system urpf") \
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


def get_md5(filename):
    """
    Fetches the md5 value from .md5 file.
    Args:
        keyword: Keyword to look for in .md5 file
        filename: .md5 filename
    """
    # Get the MD5 file
    md5_filename = "%s.md5" % filename

    if not os.path.exists(os.path.join(options["destination_path"], md5_filename)):
        abort("MD5 file is missing (%s does not exist!)"
              % os.path.join(options["destination_path"], filename))

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


def do_copy(source="", dest="", login_timeout=10, dest_tmp=""):
    """
    Copies the file provided from source to destination. Source could
    be USB or external server. Appropriate copy function is required
    based on whether the switch runs 6.x or 7.x image.
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
            copy_cmd += "copy %s://%s@%s%s %s vrf %s" % (
                protocol, user, host, source, copy_tmp, vrf)
            poap_log("Command is : %s" % copy_cmd)
            try:
                cli(copy_cmd)
            except Exception as e:
                # Remove extra junk in the message
                if "no such file" in str(e):
                    abort("Copy of %s failed: no such file" % source)
                elif "Permission denied" in str(e):
                    abort("Copy of %s failed: permission denied" % source)
                elif "No space left on device" in str(e):
                    abort("No space left on device")
                else:
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
        abort("Failed to rename %s to %s: %s" % (dest_tmp, dest, str(e)))

    poap_log("Renamed %s to %s" % (dest_tmp, dest))


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


def target_system_image_is_currently_running():
    """
    Checks if the system image that we would try to download is the one that's
    currently running. Not used if MD5 checks are enabled.
    """
    version = get_version()
    if legacy is False:
        image_parts = [part for part in re.split("[\.()]", version) if part]
        image_parts.insert(0, "nxos")
        image_parts.append("bin")

        running_image = ".".join(image_parts)

        poap_log("Running: '%s'" % running_image)
        poap_log("Target:  '%s'" % options["target_system_image"])

        return running_image == options["target_system_image"]

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

    org_file = options["destination_system_image"]
    if options["disable_md5"] is False:
        copy_md5_info(options["target_image_path"], options["target_system_image"])
        md5_sum_given = get_md5(options["target_system_image"])
        remove_file(os.path.join(options["destination_path"], "%s.md5" %
                                 options["target_system_image"]))
        poap_log("MD5 for system image from server: %s" % md5_sum_given)
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"], org_file)):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"], org_file)):
                poap_log("File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"], org_file))
                del_system_image = False
                return
        elif not md5_sum_given:
            abort("Invalid MD5 from server: %s" % md5_sum_given)
        else:
            poap_log("File %s does not exist on switch" % org_file)

    tmp_file = "%s.tmp" % org_file
    timeout = options["timeout_copy_system"]

    # For personality we use the personality path for everything
    src = os.path.join(options["target_image_path"], options["target_system_image"])

    poap_log("INFO: Starting Copy of System Image")

    do_copy(src, org_file, timeout, tmp_file)

    if options["disable_md5"] is False and md5_sum_given:
        if not verify_md5(md5_sum_given,
                          os.path.join(options["destination_path"], org_file)):
            abort("#### System file %s MD5 verification failed #####\n" % os.path.join(
                         options["destination_path"], org_file))
    poap_log("INFO: Completed Copy of System Image to %s" % os.path.join(
        options["destination_path"], org_file))


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
        if md5_sum_given and os.path.exists(os.path.join(options["destination_path"], org_file)):
            if verify_md5(md5_sum_given, os.path.join(options["destination_path"], org_file)):
                poap_log("INFO: File %s already exists and MD5 matches" %
                         os.path.join(options["destination_path"], org_file))
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
    Invoked when trying to install a 7.x image. Boot variables are
    set appropriately and the startup config is updated.
    """
    poap_log("Checking if bios upgrade is needed")
    if is_bios_upgrade_needed():
        poap_log("Installing new BIOS (will take up to 5 minutes. Don't abort)")
        install_bios()

    poap_log("Installing 7x NXOS image")

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


def verify_freespace():
    """
    Checks if the available space in bootflash is sufficient enough to
    download config and required images.
    """
    poap_log("Verifying freespace in bootflash")
    s = os.statvfs("/bootflash/")
    freespace = (s.f_bavail * s.f_frsize) / 1024
    poap_log("Free bootflash space is %s" % freespace)

    if options["required_space"] > freespace:
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
        poap_log("Router MAC conf file name : %s" % config_file)
        if os.path.exists("/usbslot%d/%s" % (usbslot, config_file)):
            options["source_config_file"] = config_file
            poap_log("Selected conf file name : %s" % options["source_config_file"])
            return
        config_file = "conf_%s.cfg" % os.environ['POAP_MGMT_MAC']
        poap_log("MGMT MAC conf file name : %s" % config_file)
        if os.path.exists("/usbslot%d/%s" % (options["usb_slot"], config_file)):
            options["source_config_file"] = config_file
            poap_log("Selected conf file name : %s" % options["source_config_file"])
            return
    else:
        if 'POAP_MAC' in os.environ:
            poap_log("Interface MAC %s" % os.environ['POAP_MAC'])
            options["source_config_file"] = "conf_%s.cfg" % os.environ['POAP_MAC']
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


def get_version():
    """
    Gets the image version of the switch from CLI.
    Output is handled differently for 6.x and 7.x version.
    """
    cli_output = cli("show version")
    if legacy:
        result = re.search(r'system.*version\s*(.*)\n', cli_output[1])
        if result is not None:
            return result.group(1)
    else:
        result = re.search(r'NXOS.*version\s*(.*)\n', cli_output)
        if result is not None:
            return result.group(1)
    poap_log("Unable to get switch version")


def get_bios_version():
    """
    Gets the BIOS version of the switch from CLI.
    Output is handled differently for 6.x and 7.x version.
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
    bios is not 3.x and image upgrade is from 6.x to 7.x
    """
    global single_image
    ver = get_version()
    bios = get_bios_version()
    poap_log("Switch is running version %s with bios version %s"
             " image %s single_image %d" % (ver, bios, options["target_system_image"],
                                            single_image))
    if re.match("nxos.7", options["target_system_image"]):
        poap_log("Upgrading to a nxos 7.x image")
        try:
            bios_number = float(bios)
        except ValueError:
            major, minor = bios.split(".", 1)
            try:
                bios_number = int(major)
            except ValueError:
                poap_log("Could not convert BIOS '%s' to a number, using text match")
                bios_number = bios

        if bios_number < 3:
            poap_log("Bios needs to be upgraded as switch is "
                     "running bios version less than 3.0")
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
    upgrade_path = [('5', '0', '3', '5', '1'), ('6', '0', '2', '6', '2'),
                    ('6', '0', '2', '6', '7')]

    major = image_info.group(1)
    minor = image_info.group(2)
    revision = image_info.group(3)
    branch = image_info.group(4)
    release = image_info.group(5)

    i = 0

    # Major
    while i < len(upgrade_path) and major > upgrade_path[i][0]:
        i += 1
    # Minor
    while i < len(upgrade_path) and minor > upgrade_path[i][1]:
        i += 1
    # Revision
    while i < len(upgrade_path) and revision > upgrade_path[i][2]:
        i += 1
    # Branch
    while i < len(upgrade_path) and branch > upgrade_path[i][3]:
        i += 1
    # Release
    while i < len(upgrade_path) and release > upgrade_path[i][4]:
        i += 1

    if i < len(upgrade_path) and major == upgrade_path[i][0] and minor == upgrade_path[i][1] \
       and revision == upgrade_path[i][2] and branch == upgrade_path[i][3] \
       and release == upgrade_path[i][4]:
        poap_log("On upgrade version")
        i += 1

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

    image_info = re.match("(\d+)\.(\d+)\((\d+)\)[A-Z](\d+)\((\w+)\)", version)
    if image_info is None:
        abort("Failed to extract image information from %s" % version)

    current_idx = find_upgrade_index_from_match(image_info)

    # Check the target image
    image_info = re.search("[\w-]+\.(\d+)\.(\d+)\.(\d+)\.[A-Z](\d+)\.(\w+)",
                           options["target_system_image"])

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
            options["target_system_image"] = match.group(1)
        # File container way
        elif os.path.basename(file_name) == "IMAGEFILE":
            options["target_system_image"] = tar.extractfile(file_name).read().strip()

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
    if options["destination_system_image"]:
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
    elif options["mode"] == "serial_number":
        set_cfg_file_serial()
    elif options["mode"] == "mac":
        set_cfg_file_mac()
    elif options["mode"] == "hostname":
        set_cfg_file_host()
    elif options["mode"] == "personality":
        initialize_personality()
    elif options["mode"] == "raw":
        # Don't need to change the name of the config file
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
    True if the target image is a 7x image.
    """
    global options, single_image

    # User wants to override the midway image
    if options["midway_system_image"] != "":
        set_next_upgrade_from_user()
    else:
        set_next_upgrade_from_upgrade_path()

    if re.match("nxos.7", options["target_system_image"]) \
       or re.match("n9000", options["target_system_image"]):
        poap_log("Single image is set")
        single_image = True
    else:
        poap_log("Single image is not set")
        single_image = False


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

    check_multilevel_install()
    # In two step install we just copy the midway image and
    # reboot. Config copy happens in the second step.
    if multi_step_install is False:
        copy_config()

    copy_system()

    if single_image is False:
        copy_kickstart()

    signal.signal(signal.SIGTERM, sig_handler_no_exit)
    # install images
    if single_image is False:
        install_images()
    else:
        install_images_7_x()

    # Cleanup midway images if any
    cleanup_temp_images()

    # Download user scripts and agents
    download_scripts_and_agents()

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
