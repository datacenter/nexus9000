"""
Script Information:
        Product Info: Nexus::9000::9516::NX-OS Release 6.2
        Category: Configuration Management
        Title: Transceiver auto speed detection and setup
        Short Description: This script is to monitor transceiver speed at all the interfaces of switch.
        Long Description: Helps in monitoring any changes in speed at any Interfaces of the switch by setting specific supported speed of the transceiver.
"""

import requests
import json
import os
import re
import ConfigParser
import datetime
import smtplib
import os.path
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nx_automation.cfg')

# Switch Host Details
ipaddress = config.get('HOSTS', 'ipaddress')
switchuser = config.get('HOSTS', 'switchusername')
switchpassword = config.get('HOSTS', 'switchpassword')

#list of to addresses for the email
to_address = config.get('EMAIL', 'to_address')

class Interface_Monit:

    global url, myheaders
    
    url='http://'+ipaddress+'/ins'
    
    # Messege Header
    myheaders={'content-type':'application/json-rpc'}

    interface_list = []
    

    # Scroll around the interfaces to monitor which interfaces have got transceivers and not
    def interfacemonit(self):
        interfaceobj = Interface_Monit()
        global bitrate, status, hostname

	# Check whether File exists or not; if yes delete.
	if os.path.exists("speed.txt"):
	    os.remove("speed.txt")

	# Enable the feature Nexus API
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "feature nxapi", "version": 1 }, "id": 2 }]
	requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

	# Get the Hostname
	cmd = "show hostname"
	payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": cmd, "version": 1 }, "id": 1 }]
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	hostname = response['result']['body']['hostname']

	# Get the available interfaces from the device
        cmd = "show interface status"
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": cmd, "version": 1 }, "id": 1 }]
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
        Interface_Monit.interface_list = response['result']['body']['TABLE_interface']['ROW_interface']
        
        for i in Interface_Monit.interface_list:
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

    # Set the Nexus Transceiver speed
    def transceiver(self, i, j, bitrate):
        interfaceobj = Interface_Monit()
	print "\nAvailable Nominal bitrate/SFP speed at interface "+str(i)+"/"+str(j)+" = "+str(bitrate)
	if (bitrate >= 100 and bitrate <= 1000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    print "Speed Set to: " + str(bitrate)
            print out
	    err = interfaceobj.error_chk(out)
            if (err == 10):
		interfaceobj.auto(i,j)
            else :
            	# Append the changes to a file
        	so = open("speed.txt","a+")
                so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with "+str(bitrate)+".\n")
                so.close()
    		
        elif (bitrate >= 1000 and bitrate <= 10000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 1000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		so = open("speed.txt","a+")
                so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with "+str(bitrate)+".\n")
                so.close()

        elif (bitrate >= 10000 and bitrate <= 40000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 10000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
		interfaceobj.auto(i,j)
	    else :
		so = open("speed.txt","a+")
                so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with "+str(bitrate)+".\n")
                so.close()

        elif (bitrate >= 40000 and bitrate <= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 40000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		so = open("speed.txt","a+")
                so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with "+str(bitrate)+".\n")
                so.close()

        elif (bitrate >= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            err = interfaceobj.error_chk(out)
            if (err == 10):
                interfaceobj.auto(i,j)
            else :
		so = open("speed.txt","a+")
                so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with "+str(bitrate)+".\n")
                so.close()

        else :
	    interfaceobj.auto(i,j)

    # Check whether the transceiver speed is different from general available set
    def error_chk(self,out):
	interfaceobj = Interface_Monit()
	ret_val = 0
	for x in out:
            for key,value in x.items():
                if (key == 'error'):
                    for a,b in value.items():
                        if (a == 'data'):
                            for c,d in b.items():
                                if (c == 'msg'):
                                    print d
                                    print "Transceiver value is set to an AUTO."
				    ret_val=10
				    return ret_val


    # Configure the interface speed to AUTO
    def auto(self, i, j):
	interfaceobj = Interface_Monit()
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed auto", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	so = open("speed.txt","a+")
        so.write("Speed at the ethernet interface "+str(i)+"/"+str(j)+" is set with AUTO.\n")
        so.close()

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
        msg['Subject'] = 'Transceiver speed update at HOST: "' + hostname + '" with IP: ' + ipaddress + ' on ' + timestamp.strftime("%d/%m/%Y") + ' @ ' + timestamp.strftime("%H:%M:%S")

	so = open("speed.txt","r")
	content = so.read()
	so.close()
	part = MIMEText(content)
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
            print "Successfully sent email"
	    print ""

        except Exception:
            print "Error: unable to send email, please check your Internet connection."
	    print ""


if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.interfacemonit()
