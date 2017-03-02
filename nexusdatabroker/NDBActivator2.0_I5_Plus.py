# -*- coding: utf-8 -*-
from cli import *
import json
import os,sys
import subprocess
import optparse
import logging
import time
import pdb
import zipfile
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
con_log_handler = logging.StreamHandler()
file_log_handler = logging.FileHandler("/bootflash/ndb_deploy.log")
file_log_handler.setLevel(logging.DEBUG)
con_log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log_handler.setFormatter(formatter)
con_log_handler.setFormatter(formatter)
logger.addHandler(file_log_handler)
logger.addHandler(con_log_handler)

def guestShell(path):
  nxosFlag = 0
  nxosVersionOut = cli("show version | inc NXOS | inc version")
  for line in nxosVersionOut.split("\n"):
      if 'inc' not in line:
          if 'I5' in line:
              nxosFlag = 1


  if nxosFlag != 1:
      logger.error("Device does not contain I5 nxos")
      sys.exit(0)

  memoryCliOuput = cli("show version | inc memory")
  for line in memoryCliOuput.split("\n"):
      line = line.strip()
      if 'inc' not in line:
          if 'memory' in line:
              nxosMemory = line.split(" ")[-4]


  try:
      if int(nxosMemory) < 8155984:
          logger.error("The device does not have sufficient memory.")
          sys.exit(0)
  except:
      logger.info("Error while verifing NXOS memory")
      sys.exit(0) 
    
   
         
 
  forceFlag = 0
  if len(sys.argv) == 4:
      zipFilePath = sys.argv[-1]
  elif len(sys.argv) == 5 and '--force' in sys.argv[-1]:
      zipFilePath = sys.argv[-2]
      forceFlag = 1
  else:
      logger.error("Please provide valid arguments")
      sys.exit(0)

  if not os.path.exists(zipFilePath):
      logger.error("Please provide valid zip file path")
      sys.exit(0)

  #Platform Verification
  devicePlatformList = []
  cliout = cli('sh ver | inc ignore-case Chassis')
  platform_flag = 0
  for line in cliout.split("\n"):
      line = line.strip()
      if ("Chassis" in line or 'chassis' in line) and 'cisco' in line:
          if len(line.split(" ")) >= 4:
              platform = line.split(" ")[2]
              platform_flag = 1
          else:
              platform = line.split(" ")[1]
              platform_flag = 1
  if platform_flag == 1:
      platform = int(re.search(r'\d+', platform).group()) 
      if str(platform)[0] == '9':
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
              logger.error("Device platform version is not N9K")
              sys.exit(0)   
  else:
      logger.error("Error while greping platform version")
      sys.exit(0)

  #Resizing the guestshell resources
  try:
      cli("guestshell enable")
  except:
      pass

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

  systemdPath = '/isan/vdc_1/virtual-instance/guestshell+/rootfs/usr/lib/systemd/system/ndb.service'
  if os.path.exists(systemdPath):
      if forceFlag == 1:
          pass
      else:
          logger.info("NDB application is already installed.")
          sys.exit(0)
  else:
      pass

  diskFreeSpace = cli("guestshell run df -m /volatile | awk '{print $4}' | grep '[0-9]'")
  diskFreeSpace = int(diskFreeSpace.strip())
  requiredSpace = 600
  if diskFreeSpace <= requiredSpace:
      logger.error("Please make sure sufficient disk space is available inside the /volatile/ folder.")
      sys.exit(0)


  try:
      cli("guestshell resize cpu 5")
  except:
      logger.error("Please provide valid CPU reservation")
      sys.exit(0)
  try:
      cli("guestshell resize memory 1536")
  except:
      logger.error("Please provide valid Memory reservation")
      sys.exit(0)
  try:
      cli("guestshell resize rootfs 1536")
  except:
     logger.error("Please provide valid Disk reservation")
     sys.exit(0)

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
  if tempflag == 1:
      logger.info("Resized the guestshell resources")

  #Unzip and place the xnc folder into the guestshell home directory
  if os.path.exists('/volatile/xnc'):
      os.system('rm -rf /volatile/xnc')

  zip_ref = zipfile.ZipFile(zipFilePath, 'r')
  zip_ref.extractall('/volatile')
  zip_ref.close()

  xncpath = '/volatile/xnc'
  cli("tar extract volatile:xnc/jre-8u121-linux-x64.tar.gz to volatile:xnc")
  os.system('rm -rf /volatile/xnc/jre-8u121-linux-x64.tar.gz')

  diskFreeSpaceInside = cli("guestshell run df -m /home/guestshell | awk '{print $4}' | grep '[0-9]'")
  diskFreeSpaceInside = int(diskFreeSpaceInside.strip())
  requiredSpaceInside = 600
  if diskFreeSpaceInside <= requiredSpaceInside:
      logger.error("Please make sure sufficient disk space is available inside the /home/guestshell/ folder.")
      sys.exit(0)

  cli("guestshell run cp -Rf "+xncpath+" /home/guestshell/")
  cli("guestshell run rm -rf "+xncpath)
  cli_cmd = "guestshell run chmod -Rf 777 /home/guestshell/xnc/"
  cli(cli_cmd)
  logger.info("Placed the xnc folder into the guestshell home directory")
  
  #Setting the nxapi to listen to network namespace 
  try:
     cli("configure terminal ; feature nxapi")
  except:
     pass
  cli("configure terminal ; nxapi use-vrf management ; copy running-config startup-config")
  logger.info("Kept the nxapi to listen to network namespace")

  cli("guestshell run /home/guestshell/xnc/embedded/i5/make-systemctl-env.sh")

def main():
    cmd_args = sys.argv
    path = cmd_args[-1]
    guestShell(path)

if __name__ == "__main__":
    main()


