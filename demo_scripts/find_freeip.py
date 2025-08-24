"""
 Cisco Nexus 9000 Switch On-Box script for finding Unused IP Addresses in the network
"""

import os,sys,re
import json
import argparse
from cli import *

"""
Class to configure the required nexus switch and perform ping test
"""

class Args(object):

    def __init__(self, args):
        self.unused_ips = []
        self.iprange = args.iprange
        fullip = '.'.join(self.iprange.split('.')[:-1])
        iprange = self.iprange.split('.')[-1].split("-")
        self.ipseries = [fullip+"."+str(n) for n in range(int(iprange[0]), int(iprange[1])+1)]
        

def print_banner():

    msg = "*"*95
    msg += '\n    Cisco Nexus 9000 Switch On-Box script for finding Unused IP Addresses in the network.\n'	
    msg += '\nDeveloped By: OneCloud Consulting\n'	
    msg += 'Please contact info@1-cloud.net for any queries.\n\n'	
    msg += "*"*95
    msg += "\n"
    print msg
	
def nexus_cli_deploy(params):	
	#execute the commands
	cmd = "conf t" + ' ' + " ;" + ' ' + "interface loopback30" + ' ' + ";" + ' ' + "ip address "+params.ipseries[1]+"/32" + ' ' + ";"
	cmd += ' ' + "interface loopback31" + ' ' + ";" + ' ' + "ip address "+params.ipseries[3]+"/32" + ' ' + ";" + ' ' + "exit" + ' ' + ";" 	
	cli(cmd)
			      

def nexus_ping(params):   
	print " * Ping Test Starts *\n" 
	for ip in params.ipseries:
		out = cli('ping %s count 1' % (ip))
		m = re.search('([0-9\.]+)% packet loss',out)
		print('%s - %s' % (ip, 'UP' if float(m.group(1)) == 0.0 else 'DOWN'))
		if float(m.group(1)) != 0.0:
			params.unused_ips.append(ip)
	print "\n * Ping Test Completed *\n"
	
	if len(params.unused_ips) > 0:
		print "*"*95
		print "\nFollowing IP Addresses are currently unused in your network:\n"
		for ip in params.unused_ips:
			print ip
		print "*"*95

def initialize_args():
	parser = argparse.ArgumentParser(
	    description='To find Unused IP Addresses in the network',
	    epilog="""   """)
	parser.add_argument('--iprange', '-ip', dest='iprange',
	    help='Please provide IP Address Range eg. 192.168.1.1-5', required=True)
	args = parser.parse_args()
	return Args(args)
    
if __name__ == '__main__':
	print_banner()
	params = initialize_args()
	nexus_cli_deploy(params)
	nexus_ping(params)
	
