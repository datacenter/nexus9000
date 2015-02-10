"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Monitoring
:Title:Interface Monitoring
:Short Description:This script is to monitor Interface counters.
:Long Description:This script is to monitor Interface counters like
Errors etc.
Input: command to check the interface status
     e.g show interface ethernet 1/1
Output : parse the json output and update the html file

"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import requests
import json
import ConfigParser
import datetime
import sys
import re

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

#switch host details
ipaddress = config.get('HostDetails', 'ipaddress')
username = config.get('HostDetails', 'username')
password = config.get('HostDetails', 'password')

#list of to addresses for the email
to_addresses = config.get('EmailDetails', 'to_addresses')

#get the current working directory
directory = os.getcwd() 
#html file location
out_template = 'interface_10.1.150.12_.jinja'
out_html = directory+'/html/interface_'+ipaddress+'_.html'


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
    print "Please update the configuration file with Switch User Creentials "
    exit(1)
elif (password == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)




"""
class to monitor the interface counters
like errors etc

"""

class Interface_Monit:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"


    in_err = {}
    out_err = {}

    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    #get the nexus switch version and chassis details
    def nexus_version(self):
        global chassis_id, sys_version
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(Interface_Monit.url,data=json.dumps(payload),headers=Interface_Monit.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']

    """
       Input: command to check the interface status
              e.g show interface ethernet 1/1
       Output : parse the json output and update the html file
    """
    def monit(self, cmd, i, j):
        
        interfaceob = Interface_Monit()    
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":cmd,"version":1},"id":1},]

        response = requests.post(Interface_Monit.url,data=json.dumps(payload),headers=Interface_Monit.myheaders,auth=(username,password)).json()
        in_err = response['result']['body']['TABLE_interface']['ROW_interface']['eth_inerr']
        out_err = response['result']['body']['TABLE_interface']['ROW_interface']['eth_outerr']
        key = str(i)+"/"+str(j)
        if (int(in_err) == 0):
            Interface_Monit.in_err.update({key:"No"})
        else:
            Interface_Monit.in_err.update({key:"Yes"})
        if (int(out_err) == 0):
            Interface_Monit.out_err.update({key:"No"})
        else:
            Interface_Monit.in_err.update({key:"Yes"})


    
    #create a command to get the interface status
    def interfacemonit(self):
        interfaceob = Interface_Monit()

        out = json.loads(clid("show interface status"))
        interface_list = out['TABLE_interface']['ROW_interface']
        for i in interface_list:
            for key,value in i.items():
                if (key == 'interface'):
                    m = re.search('Ethernet(.*)', value)
                    if m:
                        found = m.group(1)
                        slotport = found.split('/')

                        cmd = "show interface ethernet"+str(slotport[0])+"/"+str(slotport[1])
                        interfaceob.monit(cmd, slotport[0], slotport[1])



    def interfacemonit(self):
        interfaceob = Interface_Monit()
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show interface status","version":1},"id":1},]
        response = requests.post(Interface_Monit.url,data=json.dumps(payload),headers=Interface_Monit.myheaders,auth=(username,password)).json()

        interface_list = response['result']['body']['TABLE_interface']['ROW_interface']
        for i in interface_list:
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


    def updatetemp(self):
        interfaceob = Interface_Monit()
        templateVars = { "title" : "Nexus Switch Interface monitoring",
                         "description" : "Interface monitoring",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "in_err" : Interface_Monit.in_err,
                         "out_err" : Interface_Monit.out_err,
                         "input_counter" : input_counter,
                         "output_counter" : output_counter,
                         "inerr_interface" : inerr_interface,
                         "outerr_interface" : outerr_interface

        }
        with open(out_html, 'a') as f:
             outputText = interfaceob.render_template(out_template, templateVars)
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
        msg['Subject'] = 'Nexus 9000 Interface Monitoring Email' + ' ' + 'on' + ' ' + timestamp.strftime("%d/%m/%Y") + '@' + timestamp.strftime("%H:%M:%S")

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
    interfaceobj = Interface_Monit()
    interfaceobj.nexus_version()
    interfaceobj.interfacemonit()
    interfaceobj.status()
    interfaceobj.updatetemp()
    interfaceobj.send_mail()
