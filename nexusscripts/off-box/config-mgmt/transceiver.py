"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:Transceiver Auto-speed-configuration
:Short Description:This script is to auto configure the transceiver speed at all the available interfaces of switch.
:Long Description:Helps in configuring any changes in speed at any Interfaces of the switch by setting specific supported speed of the transceiver.
:Input:No Input
:Output:No Output
"""

from __future__ import print_function
import requests
import json
import os
import re
import ConfigParser
import datetime
import smtplib
import os.path
#from __future__ import print_function
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader


PATH = os.getcwd()
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False)

#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nx_automation.cfg')

# Switch Host Details
ipaddress = config.get('HOSTS', 'ipaddress')
switchuser = config.get('HOSTS', 'switchusername')
switchpassword = config.get('HOSTS', 'switchpassword')

#list of to addresses for the email
to_address = config.get('EMAIL', 'to_address')

#get the current working directory
directory = os.getcwd()
#html file and template location
out_template = 'update_intspeed.jinja'
out_html = directory+'/html/int_transciever_'+ipaddress+'_.html'

#remove the existing html file
if os.path.exists(out_html):
    os.remove(out_html)

#check the configuration details
if (ipaddress == ''):
    print ("Please update the configuration file with Switch IPAddress")
    exit(1)

if ((switchuser and switchpassword) == ''):
    print ("Please update the configuration file with Switch User Credentials")
    exit(1)
elif (switchuser == ''):
    print ("Please update the configuration file with Switch User Credentials ")
    exit(1)
elif (switchpassword == ''):
    print ("Please update the configuration file with Switch User Credentials ")
    exit(1)


class Interface_Config:

    global url, myheaders
    
    url='http://'+ipaddress+'/ins'
    
    # Messege Header
    myheaders={'content-type':'application/json-rpc'}
    speed_dict = {}
    interface_list = []
    
    def render_template(self, template_filename, context):
        return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


    # Scroll around the interfaces to configure which interfaces have got transceivers and not
    def interfaceconfig(self):
        interfaceobj = Interface_Config()
        global bitrate, status, hostname, chassis_id, sys_version


        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
		{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "feature nxapi", "version": 1 }, "id": 2 }]
	requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

	# Get the Hostname
	cmd = "show hostname"
	payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": cmd, "version": 1 }, "id": 1 }]
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	hostname = response['result']['body']['hostname']

        payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
        response = requests.post(url,data=json.dumps(payload),headers=myheaders,auth=(switchuser,switchpassword)).json()
        chassis_id = response['result']['body']['chassis_id']
        sys_version = response['result']['body']['rr_sys_ver']

	# Get the available interfaces from the device
        cmd = "show interface status"
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": cmd, "version": 1 }, "id": 1 }]
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
        Interface_Config.interface_list = response['result']['body']['TABLE_interface']['ROW_interface']
        
        for i in Interface_Config.interface_list:
            for key,value in i.items():
                if (key == 'interface'):
                    m = re.search('Ethernet(.*)', value)
                    if m:
                        found = m.group(1)
                        slotport = found.split('/')

                        cmd = "show interface ethernet"+str(slotport[0])+"/"+str(slotport[1])+"transceiver"
                        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "show interface ethernet "+str(slotport[0])+"/"+str(slotport[1])+"  transceiver", "version": 1 }, "id": 1 }]
                        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

                        status = response['result']['body']['TABLE_interface']['ROW_interface']['sfp']

                        # Check whether Transceiver is present or not at the interface
                        if (status == "present" ):
                            bitrate = response['result']['body']['TABLE_interface']['ROW_interface']['nom_bitrate']
                            interfaceobj.transceiver(slotport[0], slotport[1], bitrate);
                        else :
                            pass
	interfaceobj.send_mail()	

    # Get the Nexus Transceiver info
    def transceiver(self, i, j, bitrate):
        interfaceobj = Interface_Config()
	print ("\nAvailable Nominal bitrate/SFP speed at interface "+str(i)+"/"+str(j)+" = "+str(bitrate))

	if (bitrate >= 100 and bitrate <= 1000):
            payload=[   { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100", "version": 1 }, "id": 3 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
            if (err == 10):
		interfaceobj.auto(i,j)
            else :
    		interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with "+str(bitrate)

        elif (bitrate >= 1000 and bitrate <= 10000):
            payload=[   { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 1000", "version": 1 }, "id": 3 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with "+str(bitrate)

        elif (bitrate >= 10000 and bitrate <= 40000):
            payload=[   { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 10000", "version": 1 }, "id": 3 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
		interfaceobj.auto(i,j)
	    else :
#		key = "Ethernet"+str(i)+"/"+str(j)
#		value = "Speed is set with "+str(bitrate)
		interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with "+str(bitrate)

        elif (bitrate >= 40000 and bitrate <= 100000):
            payload=[	{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 40000", "version": 1 }, "id": 3 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 },
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with "+str(bitrate)

        elif (bitrate >= 100000):
            payload=[	{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100000", "version": 1 }, "id": 3 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, 
			{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with "+str(bitrate)

        else :
	    interfaceobj.auto(i,j)


    def error_chk(self,out):
	interfaceobj = Interface_Config()
	ret_val = 0
	for x in out:
            for key,value in x.items():
                if (key == 'error'):
                    for a,b in value.items():
                        if (a == 'data'):
                            for c,d in b.items():
                                if (c == 'msg'):
                                    print (d.replace ("ERROR", "NOTE"), end = '')
                                    print ("Transceiver value is set to an AUTO.")
				    ret_val=10
				    return ret_val


    # Configure the interface speed to AUTO
    def auto(self, i, j):
	interfaceobj = Interface_Config()
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, 
		{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, 
		{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed auto", "version": 1 }, "id": 3 }, 
		{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, 
		{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	interfaceobj.speed_dict["Ethernet"+str(i)+"/"+str(j)] = "Speed is set with AUTO."

    #update the jinja template with the data
    def updatetemp(self):
        interfaceobj = Interface_Config()
        templateVars = { "title" : "Nexus Switch Configuration management",
                         "description" : "Dynamically Update Interface Description",
                         "chassis_id" : chassis_id,
                         "os_version" : sys_version,
                         "hostname"  : hostname,
			 "ipaddress" : ipaddress,
                         "message" : interfaceobj.speed_dict
        }
        with open(out_html, 'a') as f:
             outputText = interfaceobj.render_template(out_template, templateVars)
             f.write(outputText)
	     f.close()

    # Notify the Admin about changes taken care at different interfaces.
    def send_mail(self):

        #account setup
        username = 'nexus9000.adm@gmail.com';
        password = '!cisco123';
        server = 'smtp.gmail.com:587';
        timestamp = datetime.datetime.now()

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_address
        msg['Subject'] = 'Transceiver speed updated at HOST: "' + hostname + '" with IP: ' + ipaddress + ' on ' + timestamp.strftime("%d/%m/%Y") + ' @ ' + timestamp.strftime("%H:%M:%S")
	interfaceobj.updatetemp()
	so = open(out_html,'r')
	content = so.read()
	so.close()
	part = MIMEText(content, 'html')
        msg.attach(part)
        try:
            mailserver = smtplib.SMTP(server);
            # identify ourselves to smtp gmail client
	    mailserver.ehlo();
            # secure our email with tls encryption
	    mailserver.starttls();
            # re-identify ourselves as an encrypted connection
            mailserver.ehlo();
            mailserver.login(username, password);
            mailserver.sendmail(msg['From'],(msg['To'].split(',')),msg.as_string());

            mailserver.quit();
            print ("\nSuccessfully sent email")
	    print ("")

        except Exception:
            print ("Error: unable to send email, please check your Internet connection.")
	    print ("")


if __name__ == '__main__':
    interfaceobj = Interface_Config()
    interfaceobj.interfaceconfig()
