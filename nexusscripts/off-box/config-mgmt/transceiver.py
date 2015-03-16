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
import smtplib;
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
        global bitrate, status

        cmd = "show interface status"
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "show interface status", "version": 1 }, "id": 1 }]
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
                        if (status == "present" ):
                            bitrate = response['result']['body']['TABLE_interface']['ROW_interface']['nom_bitrate']
                            interfaceobj.transceiver(slotport[0], slotport[1], bitrate);
                        else :
                            pass
		

    # Get the Nexus Transceiver info
    def transceiver(self, i, j, bitrate):
        interfaceobj = Interface_Monit()
	print "Available Nominal bitrate/SFP speed at interface "+str(i)+"/"+str(j)+" = "+str(bitrate)
	if (bitrate >= 100 and bitrate <= 1000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
		interfaceobj.auto(i,j)
            else :
		interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 1000 and bitrate <= 10000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 1000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 10000 and bitrate <= 40000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 10000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
		interfaceobj.auto(i,j)
	    else :
		interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 40000 and bitrate <= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 40000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
	    err = interfaceobj.error_chk(out)
	    if (err == 10):
                interfaceobj.auto(i,j)
            else :
		interfaceobj.send_mail(bitrate,i,j)
        else :
	    interfaceobj.auto(i,j)


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
                                    print "Setting Value of the Transceiver to an AUTO mode"
				    ret_val=10
				    return ret_val


    def auto(self, i, j):
	interfaceobj = Interface_Monit()
        payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed auto", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	out = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
        interfaceobj.send_mail("auto",i,j)


    def send_mail(self,speed,i,j):

        #account setup
        username = 'nexus9000.adm@gmail.com';
        password = '!cisco123';
        server = 'smtp.gmail.com:587';
        timestamp = datetime.datetime.now()

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_address
        msg['Subject'] = 'Nexus 9000 Transceiver Monitoring Email' + ' @ Interface ' + str(i) + '/' + str(j) + ' on ' + timestamp.strftime("%d/%m/%Y") + ' @ ' + timestamp.strftime("%H:%M:%S")

	content = "Speed of an interface is set with "+str(speed)+" at an interface ethernet "+str(i)+"/"+str(j)+"."
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
            print "Error: unable to send email at interface ethernet "+str(i)+"/"+str(j)
	    print ""


if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.interfacemonit()
