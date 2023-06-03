"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:Interface Description configuration
:Short Description:To dynamically configure interface descriptions
:Long Description:Check the CDP state and modify the interface description accordingly.
:Input:command to check the CDP state and based on the command output,
       modify the description of the interface
:Output:interface description should be updated
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import requests
import json
import ConfigParser
import datetime

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
out_template = 'update_interfacedesc.jinja'
out_html = directory+'/html/interfacedesc_'+ipaddress+'_.html'

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

Class to update the interface description based on the 
CDP state
"""

class Interface_Desc:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"
    interface_message = {}
    status = '';
    
    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    #get the nexus switch version and chassis details
    def nexus_version(self):

        global chassis_id, sys_version, hostname
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(Interface_Desc.url,data=json.dumps(payload),headers=Interface_Desc.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show hostname","version":1},"id":1},]
        response = requests.post(Interface_Desc.url,data=json.dumps(payload),headers=Interface_Desc.myheaders,auth=(username,password)).json()
        hostname =  response['result']['body']['hostname']


    def cdp_status(self):
        intob = Interface_Desc()

        #check CDP is enabled or not
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show cdp global","version":1},"id":1},]
        response = requests.post(Interface_Desc.url,data=json.dumps(payload),headers=Interface_Desc.myheaders,auth=(username,password)).json()

        if (response['result']['body']['cdp_global_enabled'] == 'enabled'):
            print "CDP is enabled on the Host Switch"

            payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show cdp nei","version":1},"id":1},]
            response = requests.post(Interface_Desc.url,data=json.dumps(payload),headers=Interface_Desc.myheaders,auth=(username,password)).json()
            status_list = response['result']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
            cdp_dict = {}

            #print status_list

            
            if (isinstance(status_list, list)):
                for i in status_list:
                    for key,value in i.items():
                        if (key == 'device_id'):
                            cdp_dict.update({key:value})
                        if (key == 'intf_id'):
                            cdp_dict.update({key:value})
                        if (key == 'port_id'):
                            cdp_dict.update({key:value})
                        #if (key == 'capability'):
                            #print value
                       #     cdp_dict.update({key:value})
                    intob.updateinterface(cdp_dict)
            elif (isinstance(status_list, dict)):
                for key,value in status_list.items():
                        if (key == 'device_id'):
                            cdp_dict.update({key:value})
                        if (key == 'intf_id'):
                            cdp_dict.update({key:value})
                        if (key == 'port_id'):
                            cdp_dict.update({key:value})
                        #if (key == 'capability'):
                            #print value
                        #    cdp_dict.update({key:value})
                intob.updateinterface(cdp_dict)
            else:
                print "Not implemented for this response type"



        else:
            print "CDP is not enabled on the Host Switch. "
            Interface_Desc.status = "CDP is not enabled on the Host Switch."
            intob.updatetemp();
            intob.send_mail()
            exit(1)





    #update the interface description  
    def updateinterface(self, data):


                
        for key,value in data.iteritems():
            if (key == 'intf_id'):
                cmd1 = "interface" + ' ' + value 
                desc = "description" + '  ' + "Connected to device" + ' ' + data['device_id'] + ' ' + "on" + ' ' + data['port_id']
                msg = "Connected to device" + '  ' + data['device_id'] + '  ' + "on" + '   ' + data['port_id']
                Interface_Desc.interface_message.update({data['intf_id']:msg})
                payload = [

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": cmd1,"version": 1},"id": 2},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": desc,"version": 1},"id": 2},        
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "exit","version": 1},"id": 2},

                         ]
                response = requests.post(Interface_Desc.url,data=json.dumps(payload),headers=Interface_Desc.myheaders,auth=(username,password)).json()
                print "\n"
                print "Interface" + ' ' + data['intf_id'] + ' ' + "description is updated as : " + ' ' + msg
                #if (data['capability']):
                #    print "Neighbor device" + ' ' + data['device_id'] + ' ' + "is capable as : "
                #    print (data['capability'])
 
    #update the jinja template with the data
    def updatetemp(self):
        systemob = Interface_Desc()
       # print Interface_Desc.interface_message
        templateVars = { "title" : "Nexus Switch Configuration management",
                         "description" : "Dynamically Update Interface Description",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "hostname"  : hostname,
                         "status" : Interface_Desc.status,
                         "message" : Interface_Desc.interface_message
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
        msg['Subject'] = 'Nexus 9000 Interface Description Update (CDP) Email' + ' ' + 'on' + ' ' + timestamp.strftime("%d/%m/%Y") + '@' + timestamp.strftime("%H:%M:%S")

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
    systemob = Interface_Desc()
    systemob.nexus_version()
    systemob.cdp_status()
    systemob.updatetemp()
    systemob.send_mail()
