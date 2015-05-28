"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Box Type:On-Box
:Title:System Resources Monitoring
:Short Description:This script is to monitor system-level resources.
:Long Description:This script is to monitor system-level resources
like cpu utilization, memory usage etc
:Input:command to check the system resources status
              e.g show system resources
:Output:parse the json output and update the html file
"""

import os,sys
import json
from cli import *


"""
class to monitor system-level resources
cpu-utilization, memory usage

"""
class System_Monit:


    cpu_utilization = {}
    mem_usage = {}



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
        print  cpu_name + ' ' + "with" + ' ' + str(memory) + ' ' + "KB of memory"
        print "Processor Board ID is " + processor_board

        print "Host Name : " + device
        print "Bootflash : " + str(bootflash) + ' ' + "KB"


    #get the monitoring data from the nexus switch
    def monit_data(self):

        out = json.loads(clid("show system resources"))
        self.cpu_kernel = out['cpu_state_kernel']
        self.cpu_idle = out['cpu_state_idle']
        self.cpu_user = out['cpu_state_user']

        #update the cpu_utilization dictionary
        System_Monit.cpu_utilization.update({'Cpu_state_kernel':self.cpu_kernel})
        System_Monit.cpu_utilization.update({'Cpu_state_idle':self.cpu_idle})
        System_Monit.cpu_utilization.update({'Cpu_state_user':self.cpu_user})


        self.mem_used = out['memory_usage_used']
        self.mem_free = out['memory_usage_free']
        self.mem_total = out['memory_usage_total']
        self.mem_status = out['current_memory_status']

        #update the memory usage dictionary
        System_Monit.mem_usage.update({'Memory_Usage_Used':self.mem_used})
        System_Monit.mem_usage.update({'Memory_Usage_Free':self.mem_free})
        System_Monit.mem_usage.update({'Memory_Usage_Total':self.mem_total})
        System_Monit.mem_usage.update({'Current_Memory_Status':self.mem_status})

    #overall cpu utilization and memory usage in percentage
    def status(self):
        global cpu_percent,mem_percent
        total_cpu = float(System_Monit.cpu_utilization['Cpu_state_kernel']) + float(System_Monit.cpu_utilization['Cpu_state_user'])
        cpu_percent = (total_cpu)/2
        print "Overall CPU Utilization is : " + str(cpu_percent) + "%"


        mem_used = float(System_Monit.mem_usage['Memory_Usage_Used']) / float(System_Monit.mem_usage['Memory_Usage_Total'])

        memory_per = mem_used*100
        mem_percent = round(memory_per,2)

        print "Overall Memory Usage (%) : " + str(mem_percent) + "%" 
        print "Overall Memory Usage (Bytes) : " + str(System_Monit.mem_usage['Memory_Usage_Used']) + \
          ' ' + "Used " + "," + ' ' + str(System_Monit.mem_usage['Memory_Usage_Free']) + ' ' + "Free " + "," + str(System_Monit.mem_usage['Memory_Usage_Total']) + \
        ' ' + "Total"


if __name__ == '__main__':
    systemob = System_Monit()
    systemob.nexus_version()
    systemob.monit_data()
    systemob.status()

