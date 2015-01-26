import requests
import json
import os
import ConfigParser

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
    def transceiver(self, i, j, speed):
        interfaceobj = Interface_Monit()
	if (int(bitrate) >= 100):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]
        elif (int(bitrate) >= 1000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 1000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]
        elif (int(bitrate) >= 10000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 10000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]
        elif (int(bitrate) >= 40000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 40000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]
        elif (int(bitrate) >= 100000):
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed 100000", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]
        else :
            payload=[{ "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "conf t", "version": 1 }, "id": 1 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "int eth "+str(i)+"/"+str(j), "version": 1 }, "id": 2 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "speed auto", "version": 1 }, "id": 3 }, { "jsonrpc": "2.0", "method": "cli", "params": { "cmd": "end", "version": 1 }, "id": 4 }]


if __name__ == '__main__':
    interfaceobj = Interface_Monit()
    interfaceobj.interfacemonit()
#    interfaceobj.transceiver(i, j, speed)
