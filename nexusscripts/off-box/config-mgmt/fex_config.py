"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:FEX configuration
:Short Description:To dynamically configure FEX
:Long Description: Check the FEX state.If not installed,install the FEX.
If not enabled ,enable the FEX.
:Input:command to check the FEX installation and based on the command output,
       install the FEX.Interfaces to be configured.
:Output:FEX should be enabled and interfaces should be configured.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os,sys
import requests
import json
import ConfigParser
import argparse
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
out_template = 'config_fex.jinja'
out_html = directory+'/html/fex_'+ipaddress+'_.html'

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
    print "Please update the configuration file with Switch User Crdentials "
    exit(1)
elif (password == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)


class Args(object):

    def __init__(self, args):
        self.interface_type = args.interface_type
        self.interface_number = args.interface_number
        self.fex_number = args.fex_number





"""

Class to install/enable FEX on the Nexus Switch
"""

class FEX_Config:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"
    earlierstat = ''; currentstat = '';
    interface_list = [];    

    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    def initialize_args(self):

        parser = argparse.ArgumentParser(
                description='Nexus 9000 FEX configuration mgmt.',
                epilog="""   """)

        parser.add_argument('--interface-type', '-t', dest='interface_type',
            help='Interface type',
            choices={'ethernet', 'port-channel'})
        parser.add_argument('--interface-number', '-s', dest='interface_number',
            help="ethernet interface slot/port")
        parser.add_argument('--fex-number', '-f', dest='fex_number',
            help="fex number")

        args = parser.parse_args()
        return Args(args)




    #get the nexus switch version and chassis details
    def nexus_version(self):

        global chassis_id, sys_version, hostname
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show hostname","version":1},"id":1},]
        response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
        hostname = response['result']['body']['hostname']


    def fex_status(self):
        fexob = FEX_Config()
        global cdp_dict
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show feature-set fex","version":1},"id":1},]
        response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
        #print response
        status = response['result']['body']['TABLE-cfcFeatureSetTable']['cfcFeatureSetOpStatus']
        FEX_Config.earlierstat = "On " + sys_version + " Nexus Switch FEX is " + status
        print FEX_Config.earlierstat
        fexob.fex_update(status)


    def fex_update(self, stat):
    
        if ((stat == 'disabled') or (stat == 'installed')) :
             payload = [

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "feature-set fex","version": 1},"id": 2},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "exit","version": 1},"id": 2},

                         ]
             response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
             FEX_Config.currentstat = "FEX is now enabled "
             print FEX_Config.currentstat

        if (stat == 'uninstalled') :
             payload = [

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "install feature-set fex","version": 1},"id": 2},
         {"jsonrpc": "2.0","method": "cli","params": {"cmd": "feature-set fex","version": 1},"id": 2},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "exit","version": 1},"id": 2},

                         ]
             response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
             FEX_Config.currentstat = "FEX is installed and enabled"
             print FEX_Config.currentstat


    def fex_inter_config(self, params):

         inter_cmd = "interface" + ' ' + params.interface_type + ' ' + params.interface_number
         fex_cmd = "fex associate" + ' ' + params.fex_number
         payload = [

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": inter_cmd,"version": 1},"id": 2},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "switchport","version": 1},"id": 3},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "switchport mode fex-fabric","version": 1},"id": 4},
        {"jsonrpc": "2.0","method": "cli","params": {"cmd": fex_cmd,"version": 1},"id": 5},

        {"jsonrpc": "2.0","method": "cli","params": {"cmd": "exit","version": 1},"id": 6},

                         ]


         response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
         #print response
         run_once = 0;
         for i in response:
             if (run_once == 0):
                 for key,value in i.items():
                     if (key == 'error'):
                         for k,v in value.items():
                             if (k == 'message'):
                                 print v + ".Interface " + params.interface_type + ' ' + params.interface_number  + '  ' + "is not configured to FEX.Check the Interface and FEX numbers are valid."
                                 run_once = run_once + 1;    


         payload = [

          {"jsonrpc": "2.0","method": "cli","params": {"cmd": "show interface fex-fabric","version": 1},"id": 1},
          ]
         response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
         
         print "Configured Interfaces to FEX :"
         status =  response['result']['body']['TABLE_fex_fabric']['ROW_fex_fabric']
         if (isinstance(status, list)):
             for i in status:
                 for key,value in i.items():
                     if (key == 'fbr_port'):
                         print value
                         FEX_Config.interface_list.append(value)
         elif (isinstance(status, dict)):
             for key,value in status.items():
                 if (key == 'fbr_port'):
                     print value
                     FEX_Config.interface_list.append(value)
         else:
             print "Not implemented for this response type"





    #update the jinja template with the data
    def updatetemp(self):
        systemob = FEX_Config()
        templateVars = { "title" : "Nexus Switch Configuration management",
                         "description" : "FEX Configuration",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "hostname" : hostname,
                         "earlierstat" : FEX_Config.earlierstat,
                         "currentstat" : FEX_Config.currentstat,
                         "interface_list" : FEX_Config.interface_list
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
        msg['Subject'] = 'Nexus 9000 FEX Configuration Email' + ' ' + 'on' + ' ' + timestamp.strftime("%d/%m/%Y") + '@' + timestamp.strftime("%H:%M:%S")

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
    systemob = FEX_Config()
    params = systemob.initialize_args()
    systemob.nexus_version()
    systemob.fex_status()
    systemob.fex_inter_config(params)
    systemob.updatetemp()
    systemob.send_mail()
