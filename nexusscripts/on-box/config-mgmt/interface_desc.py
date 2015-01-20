"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Configuration Management
:Title:Interface Description configuration
:Short Description:To dynamically configure interface descriptions
:Long Description: Check the CDP state and modify the interface description accordingly.
Input: command to check the CDP state and based on the command output,
       modify the description of the interface
Output : interface description should be updated

"""

import os
from cli import *
import sys

"""

Class to update the interface description based on the
CDP state
"""

class Interface_Desc:

    interface_message = {}

    #get the nexus switch version and chassis details
    def nexus_version(self):
        versioncmd = "show version"
        out = json.loads(clid(versioncmd))
        chassis_id = out['chassis_id']
        osversion = out['rr_sys_ver']
        print "Nexus Switch Chassis ID is :" , chassis_id
        print "OS Version is :", osversion

    def cdp_status(self):
        intob = Interface_Desc()
        cdpcmd = "show cdp nei"
        status = json.loads(clid(cdpcmd))
        status_list = status['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
#        print (status_list)
        cdp_dict = {}

        for i in status_list:
            for key,value in i.items():
                if (key == 'platform_id'):
                    cdp_dict.update({key:value})
                if (key == 'intf_id'):
                    cdp_dict.update({key:value})
                if (key == 'port_id'):
                    cdp_dict.update({key:value})

            intob.updateinterface(cdp_dict)

    #update the interface description
    def updateinterface(self, data):
        for key,value in data.iteritems():
            if (key == 'intf_id'):
                cmd1 = "interface" + ' ' + value
                desc = "description" + '  ' + "Connected to device" + ' ' + data['platform_id'] + ' ' + "on" + ' ' + data['port_id']
                msg = "Connected to device" + '  ' + data['platform_id'] + '  ' + "on" + '   ' + data['port_id']

                cmd = "conf t" + ' ' + " ;" + ' ' + cmd1 + ' ' + ";" + ' ' + desc
                #cli("conf t ; interface Ethernet 1/1 ; description testmessage ; exit")
                cli(cmd)
                print "Interface" + ' ' + data['intf_id'] + ' ' + "description is updated as : " + ' ' + msg




if __name__ == '__main__':
    interfaceob = Interface_Desc()
    interfaceob.nexus_version()
    interfaceob.cdp_status()

