"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Troubleshooting
:Title:FEX issues
:Short Description:To identify FEX issues
:Long Description: Check the FEX state
installed/enabled etc
:Input: command to check the FEX installation,
associated interfaces etc
:Output : FEX status

"""

import os,sys
import json
import ConfigParser
from cli import *


"""

Class to troubleshoot FEX on the Nexus Switch
"""

class FEX_Troubleshoot:

    stat = '';

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
        print  cpu_name + ' ' + "with" + ' ' + str(memory) + ' ' + "KB of memory"
        print "Processor Board ID is " + processor_board

        print "Host Name : " + device
        print "Bootflash : " + str(bootflash) + ' ' + "KB"


    def fex_status(self):

        out = json.loads(clid("show feature-set fex"))
        status = out['TABLE-cfcFeatureSetTable']['cfcFeatureSetOpStatus']
        FEX_Troubleshoot.stat = "On " + osversion + " Nexus Switch FEX is " + status
        print FEX_Troubleshoot.stat

    def fex_interfaces(self):

        try:
            out = json.loads(clid("show interface fex-fabric"))
            #print out
            status = out['TABLE_fex_fabric']['ROW_fex_fabric']
            FEX_Troubleshoot.stat = "On " + osversion + " Nexus Switch interfaces have detected a Fabric Extender uplink"
            print FEX_Troubleshoot.stat
            print "Interfaces configured are:"

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

        except:
            FEX_Troubleshoot.stat = "On " + osversion + " Nexus Switch interfaces are not configured to  FEX uplink"
            print FEX_Troubleshoot.stat

        #status = out['TABLE_fex_fabric']['ROW_fex_fabric']
        #print status


if __name__ == '__main__':
    systemob = FEX_Troubleshoot()
    systemob.nexus_version()
    systemob.fex_status()
    systemob.fex_interfaces()

