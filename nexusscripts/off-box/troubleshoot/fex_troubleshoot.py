"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Troubleshooting
:Title:FEX issues
:Short Description:To identify FEX issues
:Long Description: Check the FEX state
installed/enabled etc
:Input: command to check the FEX installation,
associated interfaces etc
:Output : FEX status

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
out_template = 'troubleshoot_fex.jinja'
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

Class to troubleshoot FEX on the Nexus Switch
"""

class FEX_Troubleshoot:

    stat = '';
    interface_stat = '';
    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"
    earlierstat = ''; currentstat = '';

    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    #get the nexus switch version and chassis details
    def nexus_version(self):

        global chassis_id, sys_version
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(FEX_Troubleshoot.url,data=json.dumps(payload),headers=FEX_Troubleshoot.myheaders,auth=(username,password)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']

    def fex_status(self):
        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show feature-set fex","version":1},"id":1},]
        response = requests.post(FEX_Troubleshoot.url,data=json.dumps(payload),headers=FEX_Troubleshoot.myheaders,auth=(username,password)).json()
        status = response['result']['body']['TABLE-cfcFeatureSetTable']['cfcFeatureSetOpStatus']
        FEX_Troubleshoot.stat = " FEX is " + status
        print FEX_Troubleshoot.stat

    def fex_interfaces(self):
        try:
            payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show interface fex-fabric","version":1},"id":1},]
            response = requests.post(FEX_Troubleshoot.url,data=json.dumps(payload),headers=FEX_Troubleshoot.myheaders,auth=(username,password)).json()
            
            status =  response['result']['body']['TABLE_fex_fabric']['ROW_fex_fabric']
            FEX_Troubleshoot.stat = " Interfaces have detected a Fabric Extender uplink"
            print FEX_Troubleshoot.stat
        except:
            FEX_Troubleshoot.stat = "Interfaces are not configured to  FEX uplink"
            print FEX_Troubleshoot.interface_stat






    #update the jinja template with the data
    def updatetemp(self):
        systemob = FEX_Troubleshoot()
        templateVars = { "title" : "Nexus Switch Configuration management",
                         "description" : "FEX Configuration",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "status" : FEX_Troubleshoot.stat,
                         "interface_stat" : FEX_Troubleshoot.interface_stat
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
    systemob = FEX_Troubleshoot()
    systemob.nexus_version()
    systemob.fex_status()
    systemob.fex_interfaces()
    systemob.updatetemp()
    systemob.send_mail()

