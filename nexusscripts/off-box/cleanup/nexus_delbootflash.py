"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Cleanup Script
:Title:Nexus Configuration Cleanup
:Short Description:To delete the switch bootflash configurations
:Long Description: Delete the switch bootflash configurations
:Input: command to delete the configurations
:Output: Nexus switch is cleaned up from bootflash scripts

"""

import os
import requests
import json
import ConfigParser

#read the nexus configuration file
config=ConfigParser.ConfigParser()
config.read('nexus_cleanup.cfg')

ipaddress = config.get('HostDetails', 'ipaddress')
username = config.get('HostDetails', 'username')
password = config.get('HostDetails', 'password')

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
Delete Bootflash script

"""

class Nexus_DelBootFlash:

    myheaders = {'content-type':'application/json-rpc'}

    url = "http://"+ipaddress+"/ins"


    def nexus_delbootflash(self):


        #execute the commands

	payload=[{"jsonrpc": "2.0","method": "cli","params": {"cmd": "conf t","version": 1},"id": 1},
		{"jsonrpc": "2.0","method": "cli","params": {"cmd": "terminal dont-ask","version": 1},"id": 2},
		{"jsonrpc": "2.0","method": "cli","params": {"cmd": "delete bootflash:scripts","version": 1},"id": 3}]
	response = requests.post(Nexus_DelBootFlash.url,data=json.dumps(payload), headers=Nexus_DelBootFlash.myheaders,auth=(username,password)).json()
	print response



if __name__ == '__main__':
    ob = Nexus_DelBootFlash()
    ob.nexus_delbootflash()



