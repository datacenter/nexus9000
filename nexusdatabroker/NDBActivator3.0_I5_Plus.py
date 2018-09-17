# -*- coding: utf-8 -*-
from cli import *
import json
import os
import sys
import subprocess
import optparse
import logging
import time
import pdb
import zipfile
import re
import fileinput
import signal


def test_request(arg=None):
    try:
        cli("guestshell run pwd")
        return arg
    except:
        time.sleep(11)
        return arg


class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()


if '--quiet' in sys.argv:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    con_log_handler = logging.StreamHandler()
    file_log_handler = logging.FileHandler("/bootflash/ndb_deploy.log")
    file_log_handler.setLevel(logging.DEBUG)
    con_log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)
else:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    con_log_handler = logging.StreamHandler()
    file_log_handler = logging.FileHandler("/bootflash/ndb_deploy.log")
    file_log_handler.setLevel(logging.DEBUG)
    con_log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_log_handler.setFormatter(formatter)
    con_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)
    logger.addHandler(con_log_handler)


def guestShell(path):
    # Verify command line arguments
    forceFlag = 0
    quiteFlag = 0
    if len(sys.argv) == 4:
        zipFilePath = sys.argv[-1]

    elif len(sys.argv) == 5 and '--force' in sys.argv[-1]:
        zipFilePath = sys.argv[-2]
        forceFlag = 1

    elif len(sys.argv) == 5 and '--quiet' in sys.argv[-1]:
        zipFilePath = sys.argv[-2]
        quiteFlag = 1

    elif len(sys.argv) == 6:
        zipFilePath = sys.argv[-3]
        quiteFlag = 1

    else:
        logger.error("Please provide valid arguments")
        sys.exit(0)

    # Verify zip file path
    if not os.path.exists(zipFilePath):
        logger.error("Please provide valid zip file path")
        sys.exit(0)

    # Remove if already xnc exists
    if os.path.exists('/volatile/xnc'):
        os.system('rm -rf /volatile/xnc')

    # Unzip and verify xnc is exists
    zip_ref = zipfile.ZipFile(zipFilePath, 'r')
    zip_ref.extractall('/volatile')
    zip_ref.close()
    xncpath = '/volatile/xnc'
    if not os.path.exists(xncpath):
        logger.error("Zip file doesn't contain xnc. Provide valid zip file")
        sys.exit(0)

    if not os.path.exists('/volatile/xnc/runxnc.sh'):
        logger.error("xnc doesn't contain runxnc.sh Provide valid zip file")
        sys.exit(0)

    if not os.path.exists('/volatile/xnc/start.sh'):
        logger.error("xnc doesn't contain start.sh Provide valid zip file")
        sys.exit(0)

    if not os.path.exists('/volatile/xnc/version.properties'):
        logger.error(
            "xnc doesn't contain version.properties. Provide valid zip file")
        sys.exit(0)

    if not os.path.exists('/volatile/xnc/runxnc.cmd'):
        logger.error("xnc doesn't contain runxnc.cmd Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/embedded'):
        logger.error("xnc doesn't contain embedded. Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/lib'):
        logger.error("xnc doesn't contain lib. Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/bin'):
        logger.error("xnc doesn't contain bin. Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/configuration'):
        logger.error(
            "xnc doesn't contain configuration. Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/etc'):
        logger.error("xnc doesn't contain etc. Provide valid zip file")
        sys.exit(0)

    if not os.path.isdir('/volatile/xnc/plugins'):
        logger.error("xnc doesn't contain plugins. Provide valid zip file")
        sys.exit(0)

    # Find user, Role and priveleges
    puser = subprocess.check_output("whoami", shell=True)
    try:
       whoamicliout = cli(
            "show user-account " +
            puser.split("\n")[0] +
            " | inc user")
       rolecliout = cli(
            "show user-account " +
            puser.split("\n")[0] +
            " | inc role")
       u = re.search(r'user:(.*)',whoamicliout)
       whoami = u.group(1)
       #whoami = whoamicliout.split(" ")[1]
       ro = re.search(r'roles:(.*)',rolecliout)
       userRole = ro.group(1)
       #userRole = whoamicliout.split(" ")[-1].split("\n")[0]
       userprivcliout = cli("show privilege")
       privFlag = 0
       for line in userprivcliout.split("\n"):
            line = line.strip()
            if "privilege level" in line:
                userpriv = line.split(":")[1]
                privFlag = 1
       userRole = userRole.strip()
       #print(userRole)
    except:
        logger.error("Something went wrong while finding user/role/privelege")
        sys.exit(0)

    # Verify user role
    if 'network-admin' not in userRole:
        logger.error("User role is not network-admin")
        sys.exit(0)

    # Verify user privelege
    if privFlag == 1:
        if int(userpriv) != 15:
            logger.error("User privelege is not 15")
            sys.exit(0)
    else:
        logger.error("User privelege is not 15")
        sys.exit(0)

    FirstNxosVersion = 0
    # Find NXOS version
    try:
        nxosFlag = 0
        pattern_match_flag = 0
        nxosVersionOut = cli("show version | inc NXOS | inc version")
        nxosVersionOut = nxosVersionOut.strip()
        for line in nxosVersionOut.split("\n"):
            if 'inc' not in line:
                try:
                    version_pattern = re.compile('I\d+')
                    nxos_version = version_pattern.findall(line)[0]
                    pattern_match_flag = 1
                    if int(nxos_version[1:]) >= 5:
                        nxosFlag = 1
                except:
                    pattern_match_flag = 0
                if not pattern_match_flag:
                    version_pattern = re.compile('\d+')
                    nxos_version = version_pattern.findall(line)[0]
                    pattern_match_flag = 1
                    if int(nxos_version) >= 9:
                        nxosFlag = 1
                if 'I5(1)' in line:
                    FirstNxosVersion = 1

        if nxosFlag != 1:
            logger.error("Device does not contain I5/I6/I7 nxos")
            sys.exit(0)
    except:
        logger.error("Something went wrong while finding NXOS version")
        sys.exit(0)

    # Verify guestshell commands are working
    if FirstNxosVersion != 1:
        try:
            with Timeout(10):
                test_request()

        except Timeout.Timeout:
            logger.error("Please login to the guestshell atleast once")
            sys.exit(0)

    try:
        memoryCliOuput = cli("show version | inc memory")
        for line in memoryCliOuput.split("\n"):
            line = line.strip()
            if 'inc' not in line:
                if 'memory' in line:
                    nxosMemory = line.split(" ")[-4]

        # Verify memory in the device
        try:
            if int(nxosMemory) < 8155984:
                logger.error("The device does not have sufficient memory.")
                sys.exit(0)
        except:
            logger.info("Error while verifyng NXOS memory")
            sys.exit(0)
    except:
        logger.error("Something went wrong while verifying NXOS memory")
        sys.exit(0)

    # Platform Verification
    devicePlatformList = []
    cliout = cli('sh ver | inc ignore-case Chassis')
    platform_flag = 0
    platform_string = "Platform="
    n9k_conf_flag = 0
    n3k_conf_flag = 0
    for line in cliout.split("\n"):
        line = line.strip()
        if ("Chassis" in line or 'chassis' in line) and 'cisco' in line:
            if len(line.split()) >= 4:
                platform = line.split()[2]
                platform_flag = 1
            else:
                platform = line.split()[1]
                platform_flag = 1
    if platform_flag == 1:
        platform = int(re.search(r'\d+', platform).group())
        platform_string += str(platform)+'\n'
        if str(platform)[0] == '9' or (str(platform)[0:2] == '31' and len(str(platform)) == 5):
            n9k_conf_flag = 1
        elif str(platform)[0] == '3':
            n3k_conf_flag = 1
        if str(platform)[0] in ['9', '3']:
            logger.info("Verified device platform version")
            pass
        else:
            verTempFlag = 0
            for platformVer in devicePlatformList:
                if str(platform) in platformVer:
                    verTempFlag = 1

            if verTempFlag == 1:
                logger.info("Verified device platform version")
                pass
            else:
                logger.error("Device platform version is not N9K/N3K")
                sys.exit(0)
    else:
        logger.error("Error while greping platform version")
        sys.exit(0)
    # Opening a file in xnc directory and writing the platform, flag values
    file_obj = open(xncpath+"/embedded/Platform","w+")
    n3k_string = 'n3k_conf_flag='+str(n3k_conf_flag)+'\n'
    n9k_string = 'n9k_conf_flag='+str(n9k_conf_flag)+'\n'
    L = [platform_string,n9k_string,n3k_string]
    file_obj.writelines(L)
    file_obj.close()
    # Resizing the guestshell resources
    try:
        statusFlag = 0
        try:
            output = cli("show guestshell detail | inc Activated")
            for line in output.split("\n"):
                if 'Activated' in line and 'inc' not in line:
                    statusFlag = 1
        except:
            statusFlag = 0
    except:
        logger.error("Something went wrong while verifying guestshell details")
        sys.exit(0)

    try:
        if statusFlag == 0:
            for en in range(10):
                enableFlag = 0
                try:
                    enableout = cli("guestshell enable")
                    for line in enableout.split("\n"):
                        line = line.strip()
                        if 'currently activating' in line:
                            enableFlag = 1
                    if enableFlag == 1:
                        time.sleep(5)
                    else:
                        break
                except:
                    time.sleep(5)

            tempflag = 0
            for st in range(200):
                if tempflag == 1:
                    break
                try:
                    output = cli("show guestshell detail | inc Activated")
                    for line in output.split("\n"):
                        if 'Activated' in line and 'inc' not in line:
                            tempflag += 1
                            break
                except:
                    time.sleep(1)

            if tempflag == 1:
                logger.info("Guestshell is enabled")
            else:
                logger.error("Error while enabling guestshell")
                sys.exit(0)
        else:
            logger.info("Guestshell is enabled")

    except:
        logger.error("Something went wrong while enabling guestshell")
        sys.exit(0)

    # Verifying NDB is already installed
    systemdPath = '/isan/vdc_1/virtual-instance/guestshell+/rootfs/usr/lib/systemd/system/ndb.service'
    if os.path.exists(systemdPath):
        if forceFlag == 1:
            pass
        else:
            logger.info("NDB application is already installed.")
            sys.exit(0)
    else:
        pass

    # Verify disk space insdie volatile directory

    try:
        diskFreeSpace = cli(
            "guestshell run df -m /volatile | awk '{print $4}' | grep '[0-9]'")
        diskFreeSpace = int(diskFreeSpace.strip())
        requiredSpace = 600
        if diskFreeSpace <= requiredSpace:
            logger.error(
                "Please make sure sufficient disk space is available inside the /volatile/ folder.")
            sys.exit(0)
    except:
        logger.error(
            "Something went wrong while checking disk dpace inside volatile")
        sys.exit(0)
    if n9k_conf_flag == 1 and n3k_conf_flag == 0:
        try:
            cli("guestshell resize cpu 5")
        except:
            logger.error("Please provide valid CPU reservation")
            sys.exit(0)
        try:
            cli("guestshell resize memory 1024")
        except:
            logger.error("Please provide valid Memory reservation")
            sys.exit(0)
        try:
            cli("guestshell resize rootfs 1024")
        except:
            logger.error("Please provide valid Disk reservation")
            sys.exit(0)

        try:
            cli("guestshell reboot")
            tempflag = 0
            for st in range(200):
                if tempflag == 1:
                    break
                try:
                    output = cli("show guestshell detail | inc Activated")
                    for line in output.split("\n"):
                        if 'Activated' in line and 'inc' not in line:
                            tempflag += 1
                            break
                except:
                    time.sleep(1)
        except:
            logger.error("Something went wrong while rebooting guestshell")
            sys.exit(0)

        if tempflag == 1:
            logger.info("Resized the guestshell resources")

    # Place the xnc folder into the guestshell home directory
    if FirstNxosVersion != 1:
        try: 
            makePath = '/volatile/xnc/embedded/i5/make-systemctl-env.sh'
            for line in fileinput.input(makePath, inplace=1):
                print line.replace("guestshell", whoami)

            servicePath = '/volatile/xnc/embedded/i5/ndb.service'
            for line in fileinput.input(servicePath, inplace=1):
                print line.replace("guestshell", whoami)

            runxncPath = '/volatile/xnc/embedded/i5/runxnc.sh'
            for line in fileinput.input(runxncPath, inplace=1):
                print line.replace("guestshell", whoami)

        except:
            logger.error(
                "Something went wrong while placing xnc into guestshell home directory")
            sys.exit(0)

    if FirstNxosVersion == 1:
        guestpath = "/home/guestshell"
    else:
        guestpath = "/home/" + whoami

    try:
        diskFreeSpaceInside = cli(
            "guestshell run df -m " +
            guestpath +
            " | awk '{print $4}' | grep '[0-9]'")
        diskFreeSpaceInside = int(diskFreeSpaceInside.strip())
        requiredSpaceInside = 600
        if diskFreeSpaceInside <= requiredSpaceInside:
            logger.error(
                "Please make sure sufficient disk space is available inside the /home/guestshell/ folder.")
            sys.exit(0)
    except:
        logger.error(
            "Something went wrong while checking disk space inside /home/guestshell")
        sys.exit(0)

    try:
        cli("guestshell run cp -Rf " + xncpath + " " + guestpath + "/")
        cli("guestshell run rm -rf " + xncpath)
        cli_cmd = "guestshell run chmod -Rf 777 " + guestpath + "/xnc/"
        cli(cli_cmd)
        logger.info("Placed the xnc folder into the guestshell home directory")
    except:
        logger.error(
            "Something went wrong while place xnc into guestshell home direcotry")
        sys.exit(0)

    # Setting the nxapi to listen to network namespace
    try:
        out = cli("configure terminal ; feature nxapi")
    except:
        logger.error("Something went wrong while enabling NXAPI")
        exit(0)

    try:
        cliout = cli("configure terminal ; nxapi use-vrf management ; copy running-config startup-config")
        logger.info("Kept the nxapi to listen to network namespace")
    except:
        if "Warning:" in cliout:
            logger.info("Kept the nxapi to listen to network namespace")
        else:
            logger.error(
                "Something went wrong while keeping nxapi to listen to network namespace")
            sys.exit(0)

    try:
        cli("guestshell run " + guestpath +
            "/xnc/embedded/i5/make-systemctl-env.sh")
    except:
        logger.error(
            "Something went wrong while running make-systemctl-env.sh")
        sys.exit(0)


def main():
    cmd_args = sys.argv
    path = cmd_args[-1]
    guestShell(path)

if __name__ == "__main__":

    if len(sys.argv) == 5:
        if '--quiet' in sys.argv or '--force' in sys.argv:
            pass
        else:
            logger.error("Please provide valid arguments")

    if len(sys.argv) == 6:
        if '--quiet' in sys.argv and '--force' in sys.argv:
            pass
        else:
            logger.error("Please provide valid arguments")

    main()
