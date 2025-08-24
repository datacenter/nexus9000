"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:On-Box
:Title:Transceiver auto speed detection and setup
:Short Description:This script is to monitor transceiver speed at all the interfaces of switch.
:Long Description:Helps in monitoring any changes in speed at any Interfaces of the switch by setting specific supported speed of the transceiver.
:Input:No Input
:Output:No Output
"""
from __future__ import print_function
import os,sys
import json
import re
from cli import *

cmd_config_terminal = "config terminal ;"
cmd_str_ethernet = "interface ethernet %s ;"
cmd_speed_hundred = " speed 100 ;"
cmd_speed_1k = " speed 1000 ;"
cmd_speed_10k = " speed 10000 ;"
cmd_speed_100k = " speed 100000 ;"
cmd_speed_40k = " speed 40000 ;"
cmd_speed_auto = " speed auto ;"
cmd_str_no_shutdown = " no shutdown ;"
cmd_transceiver_speed = "show interface ethernet %s/%s transceiver ;"
cmd_end = " end ;"
cmd_copy_running_startup = "copy running-config startup-config ;"
cmd_show_interface = "show running-config interface %s %s ;"


class Interface_Monit:

    interface_list = []; cmd_str = '';

    #create a command to get the interface status
    def interfacemonit(self):
        interfaceobj = Interface_Monit()


        out = json.loads(clid("show interface status"))
        Interface_Monit.interface_list = out['TABLE_interface']['ROW_interface']


        for i in Interface_Monit.interface_list:
            for key,value in i.items():
                if (key == 'interface'):
                    m = re.search('Ethernet(.*)', value)
                    if m:
                        found = m.group(1)
                        slotport = found.split('/')

                        cmd = "show interface ethernet " + str(slotport[0]) + "/" + str(slotport[1] + " transceiver")
                        out = json.loads(clid(cmd))
                        status = out['TABLE_interface']['ROW_interface']['sfp']
                        if (status == "present" ):
                            bitrate = out['TABLE_interface']['ROW_interface']['nom_bitrate']
                            interfaceobj.transceiver(slotport[0], slotport[1], int(bitrate))
                        else:
                            pass



    # Get the Nexus Transceiver info
    def transceiver(self, i, j, bitrate):
        interfaceobj = Interface_Monit()
        cmd_str = ''
        print ("\nNominal bitrate/Transceiver speed at interface " + str(i) + "/" + str(j) + " = " + str(bitrate))
        if (bitrate >= 100 and bitrate <= 1000):
            cmd_str += cmd_config_terminal
            cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
            cmd_str += cmd_speed_hundred
            cmd_str += cmd_str_no_shutdown
            cmd_str += cmd_end
            return_xml = cli(cmd_str)
            print (return_xml.replace ("ERROR", "NOTE"), end = '')
            err = re.search('ERROR(.*)', return_xml)
            if err:
                interfaceobj.auto(i,j)

        elif (bitrate >= 1000 and bitrate <= 10000):
            cmd_str += cmd_config_terminal
            cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
            cmd_str += cmd_speed_1k
            cmd_str += cmd_str_no_shutdown
            cmd_str += cmd_end
            return_xml = cli(cmd_str)
            err = re.search('ERROR(.*)', return_xml)
            print (return_xml.replace ("ERROR", "NOTE"), end = '')
            if err:
                interfaceobj.auto(i,j)

        elif (bitrate >= 10000 and bitrate <= 40000):
            cmd_str += cmd_config_terminal
            cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
            cmd_str += cmd_speed_10k
            cmd_str += cmd_str_no_shutdown
            cmd_str += cmd_end
            return_xml = cli(cmd_str)
            err = re.search('ERROR(.*)', return_xml)
            print (return_xml.replace ("ERROR", "NOTE"), end = '')
            if err:
                interfaceobj.auto(i,j)

        elif (bitrate >= 40000 and bitrate <= 100000):
            cmd_str += cmd_config_terminal
            cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
            cmd_str += cmd_speed_40k
            cmd_str += cmd_str_no_shutdown
            cmd_str += cmd_end
            return_xml = cli(cmd_str)
            err = re.search('ERROR(.*)', return_xml)
            print (return_xml.replace ("ERROR", "NOTE"), end = '')
            if err:
                interfaceobj.auto(i,j)

        elif (bitrate >= 100000):
            cmd_str += cmd_config_terminal
            cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
            cmd_str += cmd_speed_100k
            cmd_str += cmd_str_no_shutdown
            cmd_str += cmd_end
            return_xml = cli(cmd_str)
            err = re.search('ERROR(.*)', return_xml)
            print (return_xml.replace ("ERROR", "NOTE"), end = '')
            if err:
                interfaceobj.auto(i,j)

        else:
            interfaceobj.auto(i,j)


    def auto(self, i, j):
        interfaceobj = Interface_Monit()
        cmd_str = ''
        cmd_str += cmd_config_terminal
        cmd_str += cmd_str_ethernet % (str(i) +"/"+ str(j))
        cmd_str += cmd_speed_auto
        cmd_str += cmd_str_no_shutdown
        cmd_str += cmd_end
        print ("Changing Speed to AUTO")
        return_xml = cli(cmd_str)
        print (return_xml.replace ("ERROR", "NOTE"), end = '')
        
if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.interfacemonit()
    #exit(0)

