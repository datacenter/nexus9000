"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Box Type:On-Box
:Title:Interface Monitoring
:Short Description:This script is to monitor Interface counters.
:Long Description:This script is to monitor Interface counters like
Errors, Drops, Utilization etc.
:Input:command to check the interface status
     e.g show interface ethernet 1/1
:Output:Details of Drops,Errors and Utilization for all the interfaces
"""

import os,sys
import json
import re
from cli import *




"""

Class to monitor Interfaces for Input/Output
errors  on the Nexus Switch
"""

class Interface_Monit:


    in_err = {};   out_err = {}; interface_list = []; rx_tx_dict = {};


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


        """
       Input: command to check the interface status
              e.g show interface ethernet 1/1
       Output : parse the json output and update the html file
    """
    def monit(self, cmd, i, j):

        out = json.loads(clid(cmd))

        in_err = out['TABLE_interface']['ROW_interface']['eth_inerr']
        out_err = out['TABLE_interface']['ROW_interface']['eth_outerr']
        key = str(i)+"/"+str(j)
        if (int(in_err) == 0):
            Interface_Monit.in_err.update({key:"No"})
        else:
            Interface_Monit.in_err.update({key:"Yes"})
        if (int(out_err) == 0):
            Interface_Monit.out_err.update({key:"No"})
        else:
            Interface_Monit.in_err.update({key:"Yes"})


    def interface_rx_tx(self):
        table = "{0:16}{1:9}{2:9}{3:9}{4:9}{5:9}{6:9}{7:9}{8:9}"

        out = json.loads(clid("show interface status"))
        Interface_Monit.interface_list = out['TABLE_interface']['ROW_interface']


        print '----------------------------------------------------------------------------------------------------------'
        print table.format("Interface", "Rx Mbps", "Rx %", "Rx pps", "Tx Mbps", "Tx %", "Tx pps", "In Error", "Out Error")
        print '----------------------------------------------------------------------------------------------------------'

        counter = 0;
        for i in Interface_Monit.interface_list:
            for key,value in i.items():
                counter = counter+1;
                if (key == 'interface'):
                    m = re.search('Ethernet(.*)', value)
                    if m:
                        found = m.group(1)
                        slotport = found.split('/')

                        cmd = "show interface ethernet"+str(slotport[0])+"/"+str(slotport[1])
                        out = json.loads(clid(cmd))
                       
                        bw = int(out['TABLE_interface']['ROW_interface']['eth_bw'])
                        rx_bps = int(out['TABLE_interface']['ROW_interface']['eth_inrate1_bits'])
                        rx_mbps = round((rx_bps / 1000000), 1)
                        rx_pcnt = round((rx_bps / 1000) * 100 / bw, 1)
                        rx_pps = out['TABLE_interface']['ROW_interface']['eth_inrate1_pkts']

                        tx_bps = int(out['TABLE_interface']['ROW_interface']['eth_outrate1_bits'])
                        tx_mbps = round((tx_bps / 1000000), 1)
                        tx_pcnt = round((tx_bps / 1000) * 100 / bw, 1)
                        tx_pps = out['TABLE_interface']['ROW_interface']['eth_outrate1_pkts']

                        in_err = int(out['TABLE_interface']['ROW_interface']['eth_inerr'])
                        out_err = int(out['TABLE_interface']['ROW_interface']['eth_outerr'])


                        print table.format(value, str(rx_mbps), str(rx_pcnt) + '%', rx_pps, str(tx_mbps), str(tx_pcnt) + '%', tx_pps, in_err, out_err)
                        sys.stdout.flush()
               





    #create a command to get the interface status
    def interfacemonit(self):
        interfaceob = Interface_Monit()

        for i in Interface_Monit.interface_list:
            for key,value in i.items():
                if (key == 'interface'):
                    m = re.search('Ethernet(.*)', value)
                    if m:
                        found = m.group(1)
                        slotport = found.split('/')

                        cmd = "show interface ethernet"+str(slotport[0])+"/"+str(slotport[1])
                        interfaceob.monit(cmd, slotport[0], slotport[1])


    #interface monitoring status with details about input and output errors
    def status(self):
        global input_counter, output_counter, inerr_interface, outerr_interface
        input_counter = 0; output_counter=0; inerr_interface = []; outerr_interface = [];

        for key,value in Interface_Monit.in_err.items():
            if (value == "Yes"):
                input_counter = input_counter + 1;
                inerr_interface.append(key)

        for key,value in Interface_Monit.out_err.items():
            if (value == "Yes"):
                output_counter = output_counter + 1;
                outerr_interface.append(key)


        if (input_counter == 0):
            print "Number of Interfaces with Input Errors is : " + ' ' + str(input_counter)
        else:
            print "Number of Interfaces with Input Errors is : " + ' ' + str(input_counter)
            for key in inerr_interface:
                print key

        if (output_counter == 0):
            print "Number of Interfaces with Output Errors is : " + ' ' + str(output_counter)
        else:
            print "Number of Interfaces with Output Errors is : " + ' ' + str(output_counter)
            for key in outerr_interface:
                print key




if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.nexus_version()
    interfaceobj.interface_rx_tx()
    interfaceobj.interfacemonit()
    interfaceobj.status()


