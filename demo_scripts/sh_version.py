"""
 Nexus Switch Off-Box script for checking switch version.
"""

import os
import sys
import requests
import json
import argparse
import csv
from collections import namedtuple

"""
Class to configure the required nexus switch
"""
def pprinttable(rows):
	if len(rows) > 0:
		headers = rows[0]._fields
		lens = []
		for i in range(len(rows[0])):
			lens.append(len(max([x[i] for x in rows] + [headers[i]],key=lambda x:len(str(x)))))
		formats = []
		hformats = []
		for i in range(len(rows[0])):
			if isinstance(rows[0][i], int):
				formats.append("%%%dd" % lens[i])
			else:
				formats.append("%%-%ds" % lens[i])
			hformats.append("%%-%ds" % lens[i])
		pattern = " | ".join(formats)
		hpattern = " | ".join(hformats)
		separator = "-+-".join(['-' * n for n in lens])
		print hpattern % tuple(headers)
		print separator
		for line in rows:
			print pattern % tuple(line)
		print separator

      
class Nexus_Fetch_Version:
       
    myheaders = {'content-type':'application/json-rpc'}
    headers = {'content-type':'application/json'}    
    
    def __init__(self):
		self.hostlist = []
		self.hostversion = ''
		parser = argparse.ArgumentParser()
		parser.add_argument("version", help="provide version to check",type=str)
		self.args = parser.parse_args()
		self.Row = namedtuple('Row',['Host','IP_Address','Version','Matched'])
    
    def print_banner(self):
		msg = "*"*95
		msg += '\n    Cisco Nexus 9000 Switch Off-Box script for checking switch version.\n'	
		msg += '\nDeveloped By: OneCloud Consulting\n'	
		msg += 'Please contact info@1-cloud.net for any queries.\n\n'	
		msg += "*"*95
		msg += "\n"
		print msg
		print "Expected Switch Version : "+self.args.version
		
    def nexus_cli_deploy(self,host,ipaddress,username,password):
		
		url = "http://"+ipaddress+"/ins"
		#execute the commands
		try:
			payload = [{"jsonrpc":"2.0","method":"cli","params":{"cmd":"show version","version":1},"id":1},]
			response = requests.post(url,data=json.dumps(payload),headers=Nexus_Fetch_Version.myheaders,auth=(username,password)).json()
			self.hostversion = response['result']['body']['kickstart_ver_str']
			if self.args.version == self.hostversion:
				msg = "Success"
			else:
				msg = "Version not matched"
		except Exception as e:
			msg = "Error: Check Connectivity/Login/Feature NXAPI"
			pass
		self.hostlist.append(self.Row(host,ipaddress,self.hostversion,msg))		
    
    def print_result(self):
		print "\n"	
		pprinttable(self.hostlist)		
		print "\n"

if __name__ == '__main__':	
	ob = Nexus_Fetch_Version()
	ob.print_banner()
	try:
		with open('Nexus_Login_Info.csv') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				ob.nexus_cli_deploy(row['Device_Name'],row['IP_Address'],row['Username'],row['Password'])
	except IOError:
		print "Nexus_Login_Info.csv file not found and not able to read"
		print "Make sure that csv file name must be Nexus_Login_Info.csv by default with the below mentioned format"
		print "\n"
		SRow = namedtuple('SRow',['Device_Name','IP_Address','Username','Password'])
		sample = SRow('','','','')
		pprinttable([sample])	
		print "\n"
		sys.exit(0)
	ob.print_result()
	
