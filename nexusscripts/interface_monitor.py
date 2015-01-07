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
#interface slot and port details
slot = config.get('InterfaceDetails', 'slot')
startport = config.get('InterfaceDetails', 'startport')
slotoneend = config.get('InterfaceDetails', 'slotoneend')
slottwoend = config.get('InterfaceDetails', 'slottwoend')
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


if (slot == ''):
    print "Please update the configuration file with Interface Slot details"
    exit(1)


"""
class to monitor the inteface counters
like errors etc

"""

class Interface_Monit:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"

    interfaceslot = slot.split(',')
    interfaceport = []

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


    def updatetemp(self):
        interfaceob = Interface_Monit()
        templateVars = { "title" : "Nexus Switch Interface monitoring",
                         "description" : "Interface monitoring",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "slot" : Interface_Monit.interfaceslot,
                         "startport" : int(startport),
                         "slotoneend" : int(slotoneend),
                         "slottwoend" : int(slottwoend),
                         "in_err" : Interface_Monit.in_err,
                         "out_err" : Interface_Monit.out_err
        }
        with open(out_html, 'a') as f:
             outputText = interfaceob.render_template(out_template, templateVars)
             f.write(outputText)

    def send_mail(self):

        #account setup
        username = 'nexus9000.adm@gmail.com';
        password = '!cisco123';
        server = 'smtp.gmail.com:587';


        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_addresses
        msg['Subject'] = 'Nexus 9000 Interface Monitoring Email'

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
    interfaceobj.updatetemp()
    interfaceobj.send_mail()
