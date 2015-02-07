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

from cli import *


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
        cpu_name = out['cpu_name']
        memory =  out['memory']
        processor_board =  out['proc_board_id']
        device = out['host_name']
        bootflash = out['bootflash_size']

        print "Nexus Switch OS version is :" , osversion
        print "Chassis ID is :", chassis_id
        print  cpu_name + "with" + str(memory) + "KB of memory"
        print "Processor Board ID is " + processor_board

        print "Device Name : " + device
        print "Bootflash : " + str(bootflash)


    def fex_status(self):
        fexob = FEX_Config()
        global cdp_dict

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

