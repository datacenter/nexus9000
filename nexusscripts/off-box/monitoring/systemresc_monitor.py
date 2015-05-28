"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Box Type:Off-Box
:Title:System Resources Monitoring
:Short Description:This script is to monitor system-level resources.
:Long Description:This script is to monitor system-level resources 
like cpu utilization, memory usage etc
:Input:command to check the system resources status
              e.g show system resources
:Output:parse the json output and update the html file
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
import json
import ConfigParser
import datetime
import math

from jinja2 import Template
from jinja2 import Environment, FileSystemLoader

PATH = os.getcwd()
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)



#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nexus_automation.cfg')

ipaddress = config.get('HostDetails', 'ipaddress')
username = config.get('HostDetails', 'username')
password = config.get('HostDetails', 'password')

#list of to addresses for the email
to_addresses = config.get('EmailDetails', 'to_addresses')

#get the current working directory
directory = os.getcwd()
#html file and template location
out_template = 'monitor_systemresc.jinja'
out_html = directory+'/html/systemresc_'+ipaddress+'_.html'

#remove the existing html file
if (os.path.exists(out_html)):
    os.remove(out_html)

#check the configuration details
if (ipaddress == ''):
    print "Please update the configuration file with Switch IPAddress"
    exit(1)

if ((username and password) == ''):
    print "Please update the configuration file with Switch User Credentials"
    exit(1)
elif (username == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)
elif (password == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)


"""
class to monitor system-level resources
cpu-utilization, memory usage

"""

class System_Monit:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"

    cpu_utilization = {}
    mem_usage = {}
    
    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    #get the nexus switch version and chassis details
    def nexus_version(self):

        global chassis_id, sys_version
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(System_Monit.url,data=json.dumps(payload),headers=System_Monit.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']

    #get the monitoring data from the nexus switch 
    def monit_data(self):

        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show system resources","version":1},"id":1},]
        response = requests.post(System_Monit.url,data=json.dumps(payload),headers=System_Monit.myheaders,auth=(username,password)).json()
        self.cpu_kernel = response['result']['body']['cpu_state_kernel']
        self.cpu_idle = response['result']['body']['cpu_state_idle']
        self.cpu_user = response['result']['body']['cpu_state_user']

        #update the cpu_utilization dictionary
        System_Monit.cpu_utilization.update({'Cpu_state_kernel':self.cpu_kernel})
        System_Monit.cpu_utilization.update({'Cpu_state_idle':self.cpu_idle})
        System_Monit.cpu_utilization.update({'Cpu_state_user':self.cpu_user})


        self.mem_used = response['result']['body']['memory_usage_used']
        self.mem_free = response['result']['body']['memory_usage_free']
        self.mem_total = response['result']['body']['memory_usage_total']
        self.mem_status = response['result']['body']['current_memory_status']

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

        print "Overall Memory Usage is : " + str(mem_percent) + "%" + ' '+ "(" + str(System_Monit.mem_usage['Memory_Usage_Used']) + \
          ' ' + "Used in Bytes" + "/" + ' ' + str(System_Monit.mem_usage['Memory_Usage_Free']) + ' ' + "Free in Bytes" + ")"


    def updatetemp(self):
        systemob = System_Monit()
        templateVars = { "title" : "Nexus Switch System monitoring",
                         "description" : "System-Level resources monitoring",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "cpu_percent" : cpu_percent,
                         "mem_percent" : mem_percent,
                         "cpu_util" : System_Monit.cpu_utilization,
                         "mem_usage" : System_Monit.mem_usage
        }
        with open(out_html, 'a') as f:
             outputText = systemob.render_template(out_template, templateVars)
             f.write(outputText)


    def send_mail(self):

        #account setup
        username = 'nexus9000.adm@gmail.com';
        password = '!cisco123';
        server = 'smtp.gmail.com:587';
        timestamp = datetime.datetime.now()

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_addresses
        msg['Subject'] = 'Nexus 9000 System-Level Resources Monitoring Email' + ' ' + 'on' + ' ' + timestamp.strftime("%d/%m/%Y") + '@' + timestamp.strftime("%H:%M:%S")

        fp = open(out_html, 'rb')
        content = fp.read()
        part = MIMEText(content, 'html')

        msg.attach(part)

        try:
            mailserver = smtplib.SMTP(server)
            # identify ourselves to smtp gmail client
            mailserver.ehlo()
            # secure our email with tls encryption
            mailserver.starttls()
            # re-identify ourselves as an encrypted connection
            mailserver.ehlo()
            mailserver.login(username, password)

            mailserver.sendmail(msg['From'],(msg['To'].split(',')),msg.as_string())

            mailserver.quit()
            print "Successfully sent email"

        except Exception:
            print "Error: unable to send email"






if __name__ == '__main__':
    systemob = System_Monit()
    systemob.nexus_version()
    systemob.monit_data()
    systemob.status()
    systemob.updatetemp()
    systemob.send_mail()
