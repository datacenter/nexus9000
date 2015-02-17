"""
Script Information:
        Product Info: Nexus::9000::9516::NX-OS Release 6.2
        Category: Monitoring
        Title: Syslog Monitoring
        Short Description: This script is to monitor transceiver speed at all the interfaces of switch.
        Long Description: Helps in monitoring any changes in speed at any Interfaces of the switch and it also helps in altering of speed specific to respective transceiver.
        Once it changes its speed, it notifies the admin through sending a mail.
"""
import requests
import json
import os
import ConfigParser
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nx_automation.cfg')

# Switch Host Details
ipaddress = config.get('HOSTS', 'ipaddress')
switchuser = config.get('HOSTS', 'switchusername')
switchpassword = config.get('HOSTS', 'switchpassword')

#interface slot and port details
slot = config.get('INTERFACES', 'slotno')
startport = config.get('PORTS_START', 'portstart')
slotoneend = config.get('PORTS_10G', 'portoneend')
slottwoend = config.get('PORTS_40G', 'porttwoend')

#list of to addresses for the email
to_address = config.get('EMAIL', 'to_address')

class Interface_Monit:

    global url, myheaders
    
    url='http://'+ipaddress+'/ins'
    
    # Messege Header
    myheaders={'content-type':'application/json-rpc'}

    interfaceslot = slot.split(',')
    interfaceport = []

    # Scroll around the interfaces to monitor which interfaces have got transceivers and not
    def interfacemonit(self):
        interfaceobj = Interface_Monit()
        global bitrate, status

        for i in slot:
            endport = 0
            if (i == ','):
                pass
            if (i == '1'):
                endport = slotoneend
            if (i == '2'):
                endport = slottwoend
            for j in range(int(startport), int(endport)):
                cmd = "show interface ethernet"+str(i)+"/"+str(j)+"transceiver"
		payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "show interface ethernet "+str(i)+"/"+str(j)+"  transceiver", "version": 1 }, "id": 1 }]
		response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

        	status = response['result']['body']['TABLE_interface']['ROW_interface']['sfp']
		if (status == "present" ):
		    bitrate = response['result']['body']['TABLE_interface']['ROW_interface']['nom_bitrate']
                    interfaceobj.transceiver(i, j, bitrate);
		else :
		    pass
		

    # Get the Nexus Transceiver info
    def transceiver(self, i, j, bitrate):
        interfaceobj = Interface_Monit()
	print "Nominal bitrate/Transceiver speed at interface "+str(i)+"/"+str(j)+" = "+str(bitrate)
	if (bitrate >= 100 and bitrate <= 1000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
    	    interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 1000 and bitrate <= 10000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 1000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 10000 and bitrate <= 40000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 10000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 40000 and bitrate <= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 40000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            interfaceobj.send_mail(bitrate,i,j)
        elif (bitrate >= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
            interfaceobj.send_mail(bitrate,i,j)
        else :
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "configure terminal", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "interface ethernet "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed auto", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "no shutdown", "version": 1 }, "id": 4 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 5 }]
	    requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
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
        msg['Subject'] = 'Nexus 9000 Transceiver Monitoring Email' + ' ' + 'on' + ' ' + timestamp.strftime("%d/%m/%Y") + '@' + timestamp.strftime("%H:%M:%S")

	text = "Speed of a transceiver is altered with a speed of "+str(speed)+" at an interface ethernet "+str(i)+"/"+str(j)+"."
        part = MIMEText(text, 'plain')

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
            print "Error: unable to send email at interface ethernet "+str(i)+"/"+str(j)


if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.interfacemonit()
