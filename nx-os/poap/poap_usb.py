#!/bin/env python3

''' 
This script will copy the pem file to the specified location, add a trustpoint, install the certificate and abort. 
The script expects the certificates in merged pem format. 
The .cer files can be downloaded from https://www.cisco.com/security/pki/ . 
The .cer files need to be converted to .pem files, using openssl CLIs that can be run in any bash terminal. 
After the .pem files are generated, they need to be merged, and that has to be stored in the USB drive. 

For example: 
    After downloading the .cer files from above mentioned URL, these CLIs need to be run in bash. 

    openssl x509 -in crca2048.cer -out crca2048.pem -inform der
    openssl x509 -in ACT2SUDICA.cer -out ACT2SUDICA.pem -inform der
    cat crca2048.pem >> merge1.pem
    cat ACT2SUDICA.pem >> merge1.pem

This merge1.pem has to be put in the USB drive. 

'''
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

options = dict()

def set_options():
    global options
    options["destination_path"] = "poap/sudi_fs/"
    options["required_space"] = 1000
    options["final_cert"] = "final_cert.pem"


def close_log_handle():
    """
    Closes the log handle if it exists
    """
    if "log_hdl" in globals() and log_hdl != None:
        log_hdl.close()


def abort(msg=None):
    """
    Aborts the POAP script execution with an optional message.
    """
    global log_hdl

    if msg != None:
        poap_log(msg)
    cleanup_files()
    close_log_handle()
    exit(1)


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
    if "log_hdl" in globals() and log_hdl != None:
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
    if options.get(option) != None:
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
    cleanup_files()
    log_hdl.close()
    exit(1)


def poap_cleanup_script_logs():
    """
    Deletes all the POAP log files in bootflash leaving
    recent 4 files.
    """
    file_list = sorted(glob.glob(os.path.join(
        "/bootflash", '*poap*script.log')), reverse=True)
    poap_log("Found %d POAP script logs" % len(file_list))

    logs_for_removal = file_list[4:]
    for old_log in logs_for_removal:
        remove_file(old_log)


def setup_logging():
    """
    Configures the log file this script uses
    """
    global log_hdl

    #if os.environ.get("POAP_PHASE", None) == "USB":
    #    poap_script_log = "/bootflash/%s_poap_%s_usb_script.log" % (
    #        strftime("%Y%m%d%H%M%S", gmtime()),
    #        os.environ['POAP_PID'])
    #else:
    #    poap_script_log = "/bootflash/%s_poap_%s_script.log" % (strftime("%Y%m%d%H%M%S", gmtime()),
    #                                                            os.environ['POAP_PID'])

    if os.environ.get("POAP_PHASE", None) == "USB":
        poap_script_log = "/bootflash/%s_poap_usb_script.log" % (
            strftime("%Y%m%d%H%M%S", gmtime()))
    else:
        poap_script_log = "/bootflash/%s_poap_%s_script.log" % (strftime("%Y%m%d%H%M%S", gmtime()),
                                                                os.environ['POAP_PID'])
    log_hdl = open(poap_script_log, "w+")

    poap_log("Logfile name: %s" % poap_script_log)

    poap_cleanup_script_logs()

def get_version():
    """
    Gets the image version of the switch from CLI.
    """
    final_version = ""

    cli_output = cli("show version")
    result = re.search(r'NXOS.*version\s*(.*)\n', cli_output)
    #Line is of type NXOS: version <version>
    if result != None:
        interim_result = result.group()
        final_version = interim_result.replace('(', '.').replace(')', '.').replace(']', '').split()[2]

    if final_version == "":
        print("Unable to get switch version")
        return (-1,-1)

    major = final_version.split('.')[0]
    minor = final_version.split('.')[1]
    return (major,minor)


    
def trustpoint_already_present():
    cmd = "configure terminal ; show crypto ca trustpoints"
    poap_log("Executing %s" % (cmd))
    ca_check = cli(cmd)
    if '__securePOAP_USB' in ca_check:
        return True

    return False


def init_globals_and_options():
    """
    Initializes all the global variables that are used in this POAP script
    """
    global log_hdl, syslog_prefix
    global options
    # A list of valid options
    log_hdl = None
    syslog_prefix = ""
    options["destination_path"] = "poap/sudi_fs/"
    options["required_space"] = 1000
    options["final_cert"] = "final_cert.pem"

    # --- USB related settings ---
    # USB slot info. By default its USB slot 1, if not specified specifically.
    # collina2 has 2 usb ports. To enable poap in usb slot 2 user has to set the
    # value of usbslot to 2.
    slot_choice_1 = cli("dir usb1:")
    slot_choice_2 = cli("dir usb2:")
    # Check for finding whether slot 1 is empty or is an incorrect USB entered.
    if 'usb is not present' in slot_choice_1:
        if 'usb is not present' in slot_choice_2:
            poap_log(
                "Either valid USB is not entered, or inserted USB is corrupt. Please check again.")
            abort(
                "Either valid USB is not etered, or inserted USB is corrupt. Please check again.")
        else:
            options["usb_slot"] = 2

    options["usb_slot"] = 1


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

def image_supports_pem_bundle():
    major, minor = get_version()
    return ((int(major) > 10) or ((int(major) == 10) and int(minor) >=4))

def concatenate_and_make_pem_bundle():
    certificate_found = False
    dest_path = "/".join(["/bootflash", options["destination_path"]])
    poap_log("Destination file is " + str('/'.join([dest_path, options["final_cert"]])))
    dest_file = open('/'.join([dest_path, options["final_cert"]]), 'a')
    for file in os.listdir("/usbslot%s" % (options["usb_slot"])):
            if file.endswith(".pem"):
                certificate_found=True
                cert = file
                usb_path = ("/usbslot%s" % (options["usb_slot"]))
                src = open('/'.join([usb_path, file]), 'r')
                poap_log("Pem file found: " + str('/'.join([usb_path, file])))
                data = src.read()
                dest_file.write(data)
                src.close()
    
    # The pem file should now be present in the destination. 
    dest_file.close()
    return certificate_found
    
def copy_certificates_to_dest():
    certificate_found = False
    for file in os.listdir("/usbslot%s" % (options["usb_slot"])):
        if file.endswith(".pem"):
            certificate_found=True
            usb_string = ("usb%s" % (options["usb_slot"]))
            cert = file
            copy_src = ":".join([usb_string, cert])
            dest_path = ":".join(["bootflash", options["destination_path"]])
            poap_log("Copying from %s to %s" % (copy_src, dest_path))
            cmd = ("copy %s %s" % (copy_src, dest_path))
            cmd = ("configure terminal ; terminal dont-ask ; copy %s %s" % (copy_src, dest_path))
            poap_log("Formed cmd string: %s" % (cmd))
            cp_op = cli(cmd)
    
    return certificate_found


def copy_certificates():
    '''
    2 separate dest_path variables are required as shutil & os modules
    understand paths as linux paths, while copy cli requires
    path in format of bootflash:<path>
    CSCwe68911: Concatenate all pem files to form a single pem file.
    '''
    certificate_found = False
    dest_path = "/".join(["/bootflash", options["destination_path"]])
    shutil.rmtree(dest_path, ignore_errors = True)
    poap_log("Path is %s" %(dest_path))
    poap_log("Removing the destination directory to prevent installation of malicious certificates.")

    os.makedirs(dest_path)
    os.chmod(dest_path,0o777)
    
    #if os.environ.get("POAP_PHASE", None) == "USB":
    if image_supports_pem_bundle(): 
        poap_log("Pem bundle is supported.")
        certificate_found = concatenate_and_make_pem_bundle()
    else:
        poap_log("Pem bundle is not supported.")
        certificate_found = copy_certificates_to_dest()
        
    if not certificate_found:
        poap_log("No Certificate on USB drive. Please check.")
        abort("No Certificate on USB drive. Please check.")


def install_certificates():
    """
    Will install the certificates on the box
    """
    
    if image_supports_pem_bundle():
        poap_log("Pem bundle is supported.")
        certificate = os.path.join(options["destination_path"], options["final_cert"])
        poap_log("Certificate is %s" %(certificate))
        cmd = ("configure terminal ; crypto ca import __securePOAP_USB_trustpoint pkcs7 bootflash:%s force ; exit " % (certificate))
        poap_log("Trying %s" %(cmd))
        install_op = cli(cmd)
        poap_log("Install output: %s" %(install_op))
        if "could not perform CA authentication" in install_op:
            return -1
        else:
            return 0
    else:
    # Includes the case where major == -1 and minor == -1, default to the CLI which works.
        poap_log("Pem bundle is not supported.")
        for file in os.listdir(os.path.join("/bootflash", options['destination_path'])):
            if file.endswith(".pem"):
                certificate = os.path.join(options["destination_path"], file)
                cmd = ("configure terminal ; crypto ca trustpoint __securePOAP_USB_trustpoint ; exit")
                poap_log("Trying: %s " % (cmd))
                add_trustpoint_op = cli(cmd)
                cmd = ("configure terminal ; crypto ca authenticate __securePOAP_USB_trustpoint pemfile bootflash:%s ; exit" % (certificate))
                poap_log("Trying %s" %(cmd))
                install_op = cli(cmd)
                poap_log("Install output: %s" %(install_op))
                if "could not perform CA authentication" in install_op:
                    continue
                else:
                    return 0
    
    # Indicates that no certificate installation was successful
    if "could not perform CA authentication" in install_op:
        return -1

                
    
    
def main():
    signal.signal(signal.SIGTERM, sigterm_handler)
    
    if trustpoint_already_present():
        abort("Trustpoint already present. Please check. Exiting USB script.")


    poap_log("Entering USB script #######")

    #if os.environ.get("POAP_PHASE", None) != "USB":
    #    poap_log("Invalid Environment. Environment is not USB. ")
    #    abort("Invalid Environment. Environment is not USB.")

    init_globals_and_options()

    # Configure the logging for the POAP process
    setup_logging()

    # Set the prefix for syslogs based on the POAP mode
    set_syslog_prefix()

    # Verify there's enough space (and fail if not)
    verify_freespace()
    
    # No need to create the directory, since server will already be running from there
    # thereby guaranteeing the directory exists.

    # Copy the ceritficates to destination path
    copy_certificates()

    # Install the cerificates
    ret = install_certificates()
    
    if (ret == 0):
        abort("Now aborting, process was successful, but we need to abort so that DHCP phase starts.")
    else:
        abort("CA Certificate installation was unsuccessful, please unplug the USB and ensure certificates are proper.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        exc_type, exc_value, exc_tb=sys.exc_info()
        poap_log("Exception: {0} {1}".format(exc_type, exc_value))
        while exc_tb != None:
            fname=os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            poap_log("Stack - File: {0} Line: {1}"
                     .format(fname, exc_tb.tb_lineno))
            exc_tb=exc_tb.tb_next
        abort()
