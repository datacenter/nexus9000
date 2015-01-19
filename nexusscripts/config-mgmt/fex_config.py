"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Configuration Management
:Title:FEX configuration
:Short Description:To dynamically configure FEX
:Long Description: Check the FEX state.If not installed,install the FEX.
If not enabled ,enable the FEX.
Input: command to check the FEX installation and based on the command output,
       install the FEX.command to check FEX is enabled or not.
       
Output : FEX should be enabled

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
out_template = 'fex_10.1.150.12_.jinja'
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
    print "Please update the configuration file with Switch User Creentials "
    exit(1)
elif (password == ''):
    print "Please update the configuration file with Switch User Credentials "
    exit(1)


"""

Class to install/enable FEX on the Nexus Switch
"""

class FEX_Config:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"
    earlierstat = ''; currentstat = '';
    
    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    #get the nexus switch version and chassis details
    def nexus_version(self):

        global chassis_id, sys_version
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(FEX_Config.url,data=json.dumps(payload),headers=FEX_Config.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']

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
    
        if (stat == 'disabled') :
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


    #update the jinja template with the data
    def updatetemp(self):
        systemob = FEX_Config()
        templateVars = { "title" : "Nexus Switch Configuration management",
                         "description" : "FEX Configuration",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "earlierstat" : FEX_Config.earlierstat,
                         "currentstat" : FEX_Config.currentstat
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
    systemob.nexus_version()
    systemob.fex_status()
    systemob.updatetemp()
    systemob.send_mail()
