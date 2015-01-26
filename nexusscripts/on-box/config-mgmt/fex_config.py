"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Configuration Management
:Title:FEX configuration
:Short Description:To dynamically configure FEX
:Long Description: Check the FEX state.If not installed,install the FEX.
If not enabled ,enable the FEX.
Input: command to check the FEX installation and based on the command output,
       install the FEX.command to check FEX is enabled or not.

Output : FEX should be enabled

"""

import os,sys
import json
import ConfigParser
from cli import *

#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nexus_automation.cfg')

ipaddress = config.get('HostDetails', 'ipaddress')
username = config.get('HostDetails', 'username')
password = config.get('HostDetails', 'password')


#check the configuration details
if (ipaddress == ''):
    print "Please update the configuration file with Switch IPAddress"
    exit(1)

if ((username and password) == ''):
    print "Please update the configuration file with Switch User Credentials"
    exit(1)
elif (username == ''):
    print "Please update the configuration file with Switch User Creentials "
    exit(1)
elif (password == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)


"""

Class to install/enable FEX on the Nexus Switch
"""

class FEX_Config:

    earlierstat = ''; currentstat = '';

    #get the nexus switch version and chassis details
    def nexus_version(self):
        global osversion;
        versioncmd = "show version"
        out = json.loads(clid(versioncmd))
        chassis_id = out['chassis_id']
        osversion = out['rr_sys_ver']
        print "Nexus Switch Chassis ID is :" , chassis_id
        print "OS Version is :", osversion


    def fex_status(self):
        fexob = FEX_Config()

        out = json.loads(clid("show feature-set fex"))
        status = out['TABLE-cfcFeatureSetTable']['cfcFeatureSetOpStatus']
        FEX_Config.earlierstat = "On " + osversion + " Nexus Switch FEX is " + status
        print FEX_Config.earlierstat
        fexob.fex_update(status)

    def fex_update(self, stat):

        if ((stat == 'disabled') or (stat == 'installed')) :
            cli('config terminal ; feature-set fex')
            FEX_Config.currentstat = "FEX is now enabled "
            print FEX_Config.currentstat

        if (stat == 'uninstalled') :
            cmd = "conf t" + ' ' + " ;" + ' ' + "install feature-set fex" + ' ' + ";" + ' ' + "feature-set fex"
            cli(cmd)

            FEX_Config.currentstat = "FEX is installed and enabled"
            print FEX_Config.currentstat


if __name__ == '__main__':
    systemob = FEX_Config()
    systemob.nexus_version()
    systemob.fex_status()

