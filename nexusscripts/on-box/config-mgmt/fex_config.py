"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:On-Box
:Title:FEX configuration
:Short Description:To dynamically configure FEX
:Long Description:Check the FEX state.If not installed,install the FEX.
If not enabled ,enable the FEX.
:Input:command to check the FEX installation and based on the command output,
       install the FEX.Interfaces to configure to the FEX.
:Output:FEX should be enabled and interfaces should be configured.
"""

import os,sys
import json
import argparse
from cli import *


class Args(object):

    def __init__(self, args):
        self.interface_type = args.interface_type
        self.interface_number = args.interface_number
        self.fex_number = args.fex_number



"""

Class to install/enable FEX on the Nexus Switch
"""

class FEX_Config:

    earlierstat = ''; currentstat = '';


    def initialize_args(self):

        parser = argparse.ArgumentParser(
                description='Nexus 9000 FEX configuration mgmt.',
                epilog="""   """)

        parser.add_argument('--interface-type', '-t', dest='interface_type',
            help='Interface type',
            choices={'ethernet', 'port-channel'})
        parser.add_argument('--interface-number', '-s', dest='interface_number',
            help="ethernet interface slot/port")
        parser.add_argument('--fex-number', '-f', dest='fex_number',
            help="fex number")

        args = parser.parse_args()
        return Args(args)


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

    def fex_config(self, params):

         try:
            cmd = "config terminal" + ' ' + ";" + ' ' + 'interface' + ' ' + params.interface_type + params.interface_number + ' ' + ";" + ' ' + "switchport" + ' ' + ";"
             "switchport mode fex-fabric" + ' ' + ";" + ' ' +  "fex associate" + ' ' + params.fex_number + ' ' + ";" + ' '

            cli(cmd)
        except Exception as e:
            #print (e)
            if (e):
                print " Interface " + params.interface_type +  ' ' + params.interface_number + ' ' + "is not configured to FEX.Check the Interface and FEX numbers are valid."

        print "The configured interfaces are:"
        out = json.loads(clid("show interface fex-fabric"))
        #print out
        status = out['TABLE_fex_fabric']['ROW_fex_fabric']
        if (isinstance(status, list)):
            for i in status:
                for key,value in i.items():
                    if (key == 'fbr_port'):
                        print value
        elif (isinstance(status, dict)):
            for key,value in status.items():
                if (key == 'fbr_port'):
                    print value

        else:
                print "Not implemented for this response type"






if __name__ == '__main__':
    systemob = FEX_Config()
    params = systemob.initialize_args()
    systemob.nexus_version()
    systemob.fex_status()
    systemob.fex_config(params)

