"""script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:On-Box
:Title:Interface Description configuration
:Short Description:To dynamically configure interface descriptions
:Long Description:Check the LLDP state and modify the interface description accordingly.
:Input:command to check the LLDP state and based on the command output,
       modify the description of the interface
:Output:interface description should be updated
"""

import os
from cli import *
import sys

"""

Class to update the interface description based on the
LLDP state
"""

class Interface_Desc:

    interface_message = {}

    #get the nexus switch version and chassis details
    def nexus_version(self):
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

        print "Host Name : " + device
        print "Bootflash : " + str(bootflash) + ' ' + "KB"
        print "\n"


    def lldp_status(self):

        intob = Interface_Desc()

        #check lldp is enabled or not
        lldp_stat = "show lldp neighbors"
        try:
            stat = json.loads(clid(lldp_stat))
        except:
            print "LLDP is not enabled on the host switch"
            exit(1)
        if (stat):
            print "LLDP is enabled on the host switch"
            lldp_nei = "show lldp neighbors"
            status = json.loads(clid(lldp_nei))
            #print status
            status_list = status['TABLE_nbor']['ROW_nbor']
            lldp_dict = {}

            if (isinstance(status_list, list)):
                for i in status_list:
                   for key,value in i.items():
                       if (key == 'chassis_id'):
                           lldp_dict.update({'device_id':value})
                       if (key == 'l_port_id'):
                           lldp_dict.update({'intf_id':value})
                       if (key == 'port_id'):
                           lldp_dict.update({key:value})
                       if (key == 'capability'):
                           lldp_dict.update({key:''})
                   intob.updateinterface(lldp_dict)

            elif (isinstance(status_list, dict)):
                for key,value in status_list.items():
                       if (key == 'chassis_id'):
                           lldp_dict.update({'device_id':value})
                       if (key == 'l_port_id'):
                           lldp_dict.update({'intf_id':value})
                       if (key == 'port_id'):
                           lldp_dict.update({key:value})
                       if (key == 'capability'):
                           lldp_dict.update({key:''})

                intob.updateinterface(lldp_dict)
            else:
                print "Not implemented for this response type"

        else:
            print "LLDP is not enabled on the Host Switch."
            exit(1)



     #update the interface description
    def updateinterface(self, data):
        #print data
        for key,value in data.iteritems():
            if (key == 'intf_id'):
                cmd1 = "interface" + ' ' + value
                desc = "description" + '  ' + "Connected to device" + ' ' + data['device_id'] + ' ' + "on" + ' ' + data['port_id']
                msg = "Connected to device" + '  ' + data['device_id'] + '  ' + "on" + '   ' + data['port_id']

                cmd = "conf t" + ' ' + " ;" + ' ' + cmd1 + ' ' + ";" + ' ' + desc
                cli(cmd)
                print "\n"
                print "Interface" + ' ' + data['intf_id'] + ' ' + "description is updated as : " + ' ' + msg
                #if (data['capability']):
                #    print "Neighbor device" + ' ' + data['device_id'] + ' ' + "is capable as : "
                    #for i in data['capability']:
                    #    print str(i)

        #            print data['capability']



if __name__ == '__main__':
    interfaceob = Interface_Desc()
    interfaceob.nexus_version()
    interfaceob.lldp_status()

