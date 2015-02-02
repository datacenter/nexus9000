"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Title:Interface Monitoring
:Short Description:This script is to monitor Interface counters.
:Long Description:This script is to monitor Interface counters like
Errors etc.
Input: command to check the interface status
     e.g show interface ethernet 1/1
Output : Number of Input/Output Errors along with the interface
details if errorrs exists


"""

import os,sys
import json
import ConfigParser
from cli import *



#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nexus_automation.cfg')


#interface slot and port details
slot = config.get('InterfaceDetails', 'slot')
startport = config.get('InterfaceDetails', 'startport')
slotoneend = config.get('InterfaceDetails', 'slotoneend')
slottwoend = config.get('InterfaceDetails', 'slottwoend')

#check the configuration details
if (slot == ''):
    print "Please update the configuration file with Interface Slot details"
    exit(1)


"""

Class to monitor Interfaces for Input/Output
errors  on the Nexus Switch
"""

class Interface_Monit:

    interfaceslot = slot.split(',')
    interfaceport = []

    in_err = {}
    out_err = {}


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


    #read the configuration file for the slot and port details
    #create a command to get the interface status
    def interfacemonit(self):
        interfaceob = Interface_Monit()
        for i in slot:
            endport = 0
            if (i == ','):
                pass
            if (i == '1'):
                endport = slotoneend
            if (i == '2'):
                endport = slottwoend
            for j in range(int(startport), int(endport)):
                cmd = "show interface ethernet"+str(i)+"/"+str(j)
                interfaceob.monit(cmd, i, j)

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
    interfaceobj.interfacemonit()
    interfaceobj.status()


