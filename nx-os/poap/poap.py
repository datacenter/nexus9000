#!/bin/env python
#md5sum=5fddae8efacfc3b6acff9beb2a9e8bf3
# Still needs to be implemented.
# Return Values:
# 0 : Reboot and reapply configuration
# 1 : No reboot, just apply configuration. Customers issue copy file run ; copy
# run start. Do not use scheduled-config since there is no reboot needed. i.e.
# no new image was downloaded
# -1 : Error case. This will cause POAP to restart the DHCP discovery phase. 

# The above is the (embedded) md5sum of this file taken without this line, 
# can be # created this way: 
# f=poap.py ; cat $f | sed '/^#md5sum/d' > $f.md5 ; sed -i "s/^#md5sum=.*/#md5sum=$(md5sum $f.md5 | sed 's/ .*//')/" $f
# This way this script's integrity can be checked in case you do not trust
# tftp's ip checksum. This integrity check is done by /isan/bin/poap.bin).
# The integrity of the files downloaded later (images, config) is checked 
# by downloading the corresponding file with the .md5 extension and is
# done by this script itself.

import os
import time
from cli import *

# **** Here are all variables that parametrize this script **** 
# These parameters should be updated with the real values used 
# in your automation environment

# system and kickstart images, configuration: location on server (src) and target (dst)
n9k_image_version       = "6.1.2" # this must match your code version
image_dir_src           = "/tftpboot"  # Sample - /Users/bob/poap
ftp_image_dir_src_root  = image_dir_src
tftp_image_dir_src_root = image_dir_src
n9k_system_image_src    = "n9000-dk9.%s.bin" % n9k_image_version
config_file_src         = "/tftpboot/conf" # Sample - /Users/bob/poap/conf
image_dir_dst           = "bootflash:poap" # directory where n9k image will be stored
system_image_dst        = n9k_system_image_src
config_file_dst         = "volatile:poap.cfg"
md5sum_ext_src          = "md5"
# Required space on /bootflash (for config and system images)
required_space          = 350000

# copy protocol to download images and config
# options are: scp/http/tftp/ftp/sftp
protocol                = "scp" # protocol to use to download images/config

# Host name and user credentials
username                = "root" # server account
ftp_username            = "anonymous" # server account
password                = "root" # password
hostname                = "1.1.1.1" # ip address of ftp/scp/http/sftp server

# vrf info
vrf = "management"
if os.environ.has_key('POAP_VRF'):
    vrf=os.environ['POAP_VRF']

# Timeout info (from biggest to smallest image, should be f(image-size, protocol))
system_timeout          = 2100 
config_timeout          = 120 
md5sum_timeout          = 120  

# POAP can use 3 modes to obtain the config file.
# - 'static' - filename is static
# - 'serial_number' - switch serial number is part of the filename
# - 'location' - CDP neighbor of interface on which DHCPDISCOVER arrived
#                is part of filename
# if serial-number is abc, then filename is $config_file_src.abc
# if cdp neighbor's device_id=abc and port_id=111, then filename is config_file_src.abc.111
# Note: the next line can be overwritten by command-line arg processing later
config_file_type        = "static"

# parameters passed through environment:
# TODO: use good old argv[] instead, using env is bad idea.
# pid is used for temp file name: just use getpid() instead!
# serial number should be gotten from "show version" or something!
pid=""
if os.environ.has_key('POAP_PID'):
    pid=os.environ['POAP_PID']
serial_number=None
if os.environ.has_key('POAP_SERIAL'):
    serial_number=os.environ['POAP_SERIAL']
cdp_interface=None
if os.environ.has_key('POAP_INTF'):
    cdp_interface=os.environ['POAP_INTF']

# will append date/timespace into the name later
log_filename = "/bootflash/poap.log"
t=time.localtime()
now="%d_%d_%d" % (t.tm_hour, t.tm_min, t.tm_sec)
#now=None
#now=1 # hardcode timestamp (easier while debugging)

# **** end of parameters **** 
# *************************************************************

# ***** argv parsing and online help (for test through cli) ******
# ****************************************************************

# poap.bin passes args (serial-number/cdp-interface) through env var
# for no seeminly good reason: we allow to overwrite those by passing
# argv, this is usufull when testing the script from vsh (even simple
# script have many cases to test, going through a reboto takes too long)

import sys
import re

cl_cdp_interface=None  # Command Line version of cdp-interface
cl_serial_number=None  # can overwrite the corresp. env var
cl_protocol=None       # can overwride the script's default
cl_download_only=None  # dont write boot variables

def parse_args(argv, help=None):
    global cl_cdp_interface, cl_serial_number, cl_protocol, protocol, cl_download_only
    while argv:
        x = argv.pop(0)
        # not handling duplicate matches...
        if cmp('cdp-interface'[0:len(x)], x) == 0:
          try: cl_cdp_interface = argv.pop(0)
          except: 
             if help: cl_cdp_interface=-1
          if len(x) != len('cdp-interface') and help: cl_cdp_interface=None
          continue
        if cmp('serial-number'[0:len(x)], x) == 0:
          try: cl_serial_number = argv.pop(0)
          except: 
            if help: cl_serial_number=-1
          if len(x) != len('serial-number') and help: cl_serial_number=None
          continue
        if cmp('protocol'[0:len(x)], x) == 0:
          try: cl_protocol = argv.pop(0); 
          except: 
            if help: cl_protocol=-1
          if len(x) != len('protocol') and help: cl_protocol=None
          if cl_protocol: protocol=cl_protocol
          continue
        if cmp('download-only'[0:len(x)], x) == 0:
          cl_download_only = 1
          continue
        print "Syntax Error|invalid token:", x
        exit(-1)
  

########### display online help (if asked for) #################
nb_args = len(sys.argv)
if nb_args > 1:
  m = re.match('__cli_script.*help', sys.argv[1])
  if m:
    # first level help: display script description
    if sys.argv[1] == "__cli_script_help":
      print "loads system/kickstart images and config file for POAP\n"
      exit(0)
    # argument help
    argv = sys.argv[2:]
    # dont count last arg if it was partial help (no-space-question-mark)
    if sys.argv[1] == "__cli_script_args_help_partial":
      argv = argv[:-1]
    parse_args(argv, "help")
    if cl_serial_number==-1:
      print "WORD|Enter the serial number"
      exit(0)
    if cl_cdp_interface==-1:
      print "WORD|Enter the CDP interface instance"
      exit(0)
    if cl_protocol==-1:
      print "tftp|Use tftp for file transfer protocol"
      print "ftp|Use ftp for file transfer protocol"
      print "scp|Use scp for file transfer protocol"
      exit(0)
    if not cl_serial_number:
      print "serial-number|The serial number to use for the config filename"
    if not cl_cdp_interface:
      print "cdp-interface|The CDP interface to use for the config filename"
    if not cl_protocol:
      print "protocol|The file transfer protocol"
    if not cl_download_only:
      print "download-only|stop after download, dont write boot variables"
    print "<CR>|Run it (use static name for config file)"
    # we are done
    exit(0)

# *** now overwrite env vars with command line vars (if any given)
# if we get here it is the real deal (no online help case)

argv = sys.argv[1:]
parse_args(argv)
if cl_serial_number: 
    serial_number=cl_serial_number
    config_file_type = "serial_number"
if cl_cdp_interface: 
    cdp_interface=cl_cdp_interface
    config_file_type = "location"
if cl_protocol: 
    protocol=cl_protocol


# setup log file and associated utils

if now == None:
  now=cli("show clock | sed 's/[ :]/_/g'");
try:
    log_filename = "%s.%s" % (log_filename, now)
except Exception as inst:
    print inst
poap_log_file = open(log_filename, "w+")

def poap_log (info):
    poap_log_file.write(info)
    poap_log_file.write("\n")
    poap_log_file.flush()
    print "poap_py_log:" + info
    sys.stdout.flush()

def poap_log_close ():
    poap_log_file.close()

def abort_cleanup_exit () : 
    poap_log("INFO: cleaning up")
    poap_log_close()
    exit(-1)


# some argument sanity checks:

if config_file_type == "serial_number" and serial_number == None: 
    poap_log("ERR: serial-number required (to derive config name) but none given")
    exit(-1)

if config_file_type == "location" and cdp_interface == None: 
    poap_log("ERR: interface required (to derive config name) but none given")
    exit(-1)

# figure out what kind of box we have (to download the correct image)
try: 
  r=clid("show version")
  m = re.match('Nexus9000', r["chassis_id/1"])
  if m:
    box="n9k"
  else:
    m = re.match('Nexus7000', r["chassis_id"])
    if m: 
      box="n7k"
      m = re.match('.*module-2', r["module_id"])
      if m: box="n7k2"
    else: box="n9k"
except: box="n9k"
print "box is", box

# get final image name based on actual box
system_image_src    = eval("%s_%s" % (box , "system_image_src"), globals())
try: root_path      = eval("%s_%s" % (protocol , "image_dir_src_root"), globals())
except: root_path   = ""
try: username       = eval("%s_%s" % (protocol , "username"), globals())
except: pass

# images are copied to temporary location first (dont want to 
# overwrite good images with bad ones).
system_image_dst_tmp    = "%s%s/%s"     % (image_dir_dst, ".new", system_image_dst)
system_image_dst        = "%s/%s"       % (image_dir_dst, system_image_dst)

system_image_src        = "%s/%s"       % (image_dir_src, system_image_src)

# cleanup stuff from a previous run
# by deleting the tmp destination for image files and then recreating the
# directory
image_dir_dst_u="/%s" % image_dir_dst.replace(":", "/") # unix path: cli's rmdir not working!

import shutil
try: shutil.rmtree("%s.new" % image_dir_dst_u)
except: pass
os.mkdir("%s.new" % image_dir_dst_u)

if not os.path.exists(image_dir_dst_u):
    os.mkdir(image_dir_dst_u)

import signal
import string

# Set CDP variables for location option
# Will be used by set_config_file_src_location() function
poap_log("INFO: show cdp neighbors interface %s" % cdp_interface)
a = clid("show cdp neighbors interface %s" % cdp_interface)
b = eval(a)
cdpnei_switchName = b['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']['device_id']
cdpnei_intfName = b['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']['port_id']
cdpnei_intfName = string.replace(cdpnei_intfName, "/", "_")

# utility functions

def run_cli (cmd):
    poap_log("CLI : %s" % cmd)
    return cli(cmd)

def rm_rf (filename): 
    try: cli("delete %s" % filename)
    except: pass

# signal handling

def sig_handler_no_exit (signum, frame) : 
    poap_log("INFO: SIGTERM Handler while configuring boot variables")

def sigterm_handler (signum, frame): 
    poap_log("INFO: SIGTERM Handler") 
    abort_cleanup_exit()
    exit(1)

signal.signal(signal.SIGTERM, sigterm_handler)

# transfers file, return True on success; on error exits unless 'fatal' is False in which case we return False
def doCopy (protocol = "", host = "", source = "", dest = "", vrf = "management", login_timeout=10, user = "", password = "", fatal=True):
    rm_rf(dest)

    # mess with source paths (tftp does not like full paths)
    global username, root_path
    source = source[len(root_path):]

    cmd = "terminal dont-ask ; terminal password %s ; " % password
    cmd += "copy %s://%s@%s%s %s vrf %s" % (protocol, username, host, source, dest, vrf)

    try: run_cli(cmd)
    except:
        poap_log("WARN: Copy Failed: %s" % str(sys.exc_value).strip('\n\r'))
        if fatal:
            poap_log("ERR : aborting")
            abort_cleanup_exit()
            exit(1)
        return False
    return True


def get_md5sum_src (file_name):
    md5_file_name_src = "%s.%s" % (file_name, md5sum_ext_src)
    md5_file_name_dst = "volatile:%s.poap_md5" % os.path.basename(md5_file_name_src)
    rm_rf(md5_file_name_dst)

    ret=doCopy(protocol, hostname, md5_file_name_src, md5_file_name_dst, vrf, md5sum_timeout, username, password, False)
    if ret == True:
        sum=run_cli("show file %s | grep -v '^#' | head lines 1 | sed 's/ .*$//'" % md5_file_name_dst).strip('\n')
        poap_log("INFO: md5sum %s (.md5 file)" % sum)
        rm_rf(md5_file_name_dst)
        return sum
    return None
    # if no .md5 file, and text file, could try to look for an embedded checksum (see below)


def check_embedded_md5sum (filename):
    # extract the embedded checksum
    sum_emb=run_cli("show file %s | grep '^#md5sum' | head lines 1 | sed 's/.*=//'" % filename).strip('\n')
    if sum_emb == "":
        poap_log("INFO: no embedded checksum")
        return None
    poap_log("INFO: md5sum %s (embedded)" % sum_emb)

    # remove the embedded checksum (create temp file) before we recalculate
    cmd="show file %s exact | sed '/^#md5sum=/d' > volatile:poap_md5" % filename
    run_cli(cmd)
    # calculate checksum (using temp file without md5sum line)
    sum_dst=run_cli("show file volatile:poap_md5 md5sum").strip('\n')
    poap_log("INFO: md5sum %s (recalculated)" % sum_dst)
    try: run_cli("delete volatile:poap_md5")
    except: pass
    if sum_emb != sum_dst:
        poap_log("ERR : MD5 verification failed for %s" % filename)
        abort_cleanup_exit()

    return None

def get_md5sum_dst (filename):
    sum=run_cli("show file %s md5sum" % filename).strip('\n')
    poap_log("INFO: md5sum %s (recalculated)" % sum)
    return sum  

def check_md5sum (filename_src, filename_dst, lname):
    md5sum_src = get_md5sum_src(filename_src)
    if md5sum_src: # we found a .md5 file on the server
        md5sum_dst = get_md5sum_dst(filename_dst)
        if md5sum_dst != md5sum_src:
            poap_log("ERR : MD5 verification failed for %s! (%s)" % (lname, filename_dst))
            abort_cleanup_exit()

def same_images (filename_src, filename_dst):
    if os.path.exists(image_dir_dst_u):
        md5sum_src = get_md5sum_src(filename_src)
        if md5sum_src:
            md5sum_dst = get_md5sum_dst(filename_dst)
            if md5sum_dst == md5sum_src:
                poap_log("INFO: Same source and destination images" ) 
                return True
    poap_log("INFO: Different source and destination images" ) 
    return False

# Will run our CLI command to test MD5 checksum and if files are valid images
# This check is also performed while setting the boot variables, but this is an
# additional check

def get_version (msg):
    lines=msg.split("\n") 
    for line in lines:
        index=line.find("MD5")
        if (index!=-1):
            status=line[index+17:]

        index=line.find("kickstart:")
        if (index!=-1): 
            index=line.find("version")
            ver=line[index:]
            return status,ver

        index=line.find("system:")
        if (index!=-1):
            index=line.find("version")
            ver=line[index:]
            return status,ver
    
def verify_images2 ():
    sys_cmd="show version image %s" % system_image_dst
    sys_msg=cli(sys_cmd)

    sys_s,sys_v=get_version(sys_msg)    
    
    print "Value: %s and %s" % (kick_s, sys_s)
    if (kick_s == "Passed" and sys_s == "Passed"):
        # MD5 verification passed
        if(kick_v != sys_v): 
            poap_log("ERR : Image version mismatch. (kickstart : %s) (system : %s)" % (kick_v, sys_v))
            abort_cleanup_exit()
    else:
        poap_log("ERR : MD5 verification failed!")
        poap_log("%s\n%s" % (kick_msg, sys_msg))
        abort_cleanup_exit()
    poap_log("INFO: Verification passed. (kickstart : %s) (system : %s)" % (kick_v, sys_v))
    return True

def verify_images ():
    print "show version image %s" % system_image_dst
    sys_cmd="show version image %s" % system_image_dst
    sys_msg=cli(sys_cmd)
    sys_v=sys_msg.split()
    print "system image Values: %s " % (sys_v[2])
    print "system image Values v10 is : %s" % (sys_v[10])
    if (sys_v[2] == "Passed"):
        poap_log("INFO: Verification passed. (system : %s)" % (sys_v[10]))
    else:
        poap_log("ERR : MD5 verification failed!")
        poap_log("%s" % (sys_msg))
        abort_cleanup_exit()
    poap_log("INFO: Verification passed.  (system : %s)" % (sys_v[10]))
    return True

# get config file from server
def get_config ():
    doCopy(protocol, hostname, config_file_src, config_file_dst, vrf, config_timeout, username, password)
    poap_log("INFO: Completed Copy of Config File") 
    # get file's md5 from server (if any) and verify it, failure is fatal (exit)
    check_md5sum (config_file_src, config_file_dst, "config file")


# get system image file from server
def get_system_image ():
    if not same_images(system_image_src, system_image_dst):
        doCopy(protocol, hostname, system_image_src, system_image_dst_tmp, vrf, system_timeout, username, password)  
        poap_log("INFO: Completed Copy of System Image" ) 
        # get file's md5 from server (if any) and verify it, failure is fatal (exit)
        check_md5sum(system_image_src, system_image_dst_tmp, "system image")
        run_cli("move %s %s" % (system_image_dst_tmp, system_image_dst))


def wait_box_online ():
    while 1:
        r=int(run_cli("show system internal platform internal info | grep box_online | sed 's/[^0-9]*//g'").strip('\n'))
        if r==1: break
        else: time.sleep(5)
        poap_log("INFO: Waiting for box online...")


# install (make persistent) images and config 
def install_it (): 
    global cl_download_only
    if cl_download_only: exit(0)
    timeout = -1

    # make sure box is online
    wait_box_online()

    poap_log("INFO: Setting the boot variables")
    try: shutil.rmtree("%s.new" % image_dir_dst_u)
    except: pass
    try:
        run_cli("config terminal ; boot nxos %s" % system_image_dst)
        run_cli("copy running-config startup-config")
        run_cli('copy %s scheduled-config' % config_file_dst)
    except:
        poap_log("ERR : setting bootvars or copy run start failed!")
        abort_cleanup_exit()
    # no need to delete config_file_dst, it is in /volatile and we will reboot....
    # do it anyway so we don't have permission issues when testing script and
    # running as different users (log file have timestamp, so fine)
    poap_log("INFO: Configuration successful")

        
# Verify if free space is available to download config, kickstart and system images
def verify_freespace (): 
    freespace = int(cli("dir bootflash: | last 3 | grep free | sed 's/[^0-9]*//g'").strip('\n'))
    freespace = freespace / 1024
    poap_log("INFO: free space is %s kB"  % freespace )

    if required_space > freespace:
        poap_log("ERR : Not enough space to copy the config, kickstart image and system image, aborting!")
        abort_cleanup_exit()

# figure out config filename to download based on CDP Neighbor information
def set_config_file_src_location():
    global config_file_src, cdpnei_switchName, cdpnei_intfName
    config_file_src = "%s.%s.%s" % (config_file_src, cdpnei_switchName, cdpnei_intfName)
    poap_log("INFO: Selected conf file name (location) : %s" % config_file_src)

# figure out config filename to download based on serial-number
def set_config_file_src_serial_number (): 
    global config_file_src
    config_file_src = "%s.%s" % (config_file_src, serial_number)
    poap_log("INFO: Selected config filename (serial_number) : %s" % config_file_src)

if config_file_type == "location":
    # set source config file based on switch's location
    set_config_file_src_location()

if config_file_type == "serial_number": 
    #set source config file based on switch's serial number
    set_config_file_src_serial_number()


# finally do it

verify_freespace()
get_system_image()
verify_images()
get_config()

# don't let people abort the final stage that concretize everything
# not sure who would send such a signal though!!!! (sysmgr not known to care about vsh)
signal.signal(signal.SIGTERM, sig_handler_no_exit)
install_it()

poap_log_close()
exit(0)

