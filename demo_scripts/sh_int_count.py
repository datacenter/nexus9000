"""
 Cisco Nexus 9000 Switch On-Box script for monitoring interface RX counter.
"""

import os,sys,re
import json
import argparse
import time
from cli import *

"""
Class to configure the required nexus switch and monitor interface RX counter
"""

class Args(object):

    def __init__(self, args):
        self.interfacename = args.interfacename   
        self.nooftimes = args.nooftimes    
        self.delay = args.delay		   
        self.log = args.log		

def print_banner(params, outfile):

    msg = "*"*95
    msg += '\n    Cisco Nexus 9000 Switch On-Box script for Monitoring Interface RX Counter.\n'	
    msg += '\nDeveloped By: OneCloud Consulting\n'	
    msg += 'Please contact info@1-cloud.net for any queries.\n\n'	
    msg += "*"*95
    msg += "\n"
    print msg
    if params.log == 'yes':
	    outfile.write(msg)
	
def nexus_cli_deploy(params, outfile):			
	if int(params.nooftimes) > 0:
		nooftimes = int(params.nooftimes)
	else:
		nooftimes = 1	
		
	if int(params.delay) > 0:
		delay = int(params.delay)
	else:
		delay = 1
		
	for i in range(nooftimes):		
		#execute the commands
		msg = "Iteration No: "+str(i+1)
		interface_data = json.loads(clid('show interface '+params.interfacename))
		msg += "RX "+interface_data['TABLE_interface']['ROW_interface']['eth_inucast']+" packets\n"
		print msg
		if params.log == 'yes':
			outfile.write(msg)
		time.sleep(delay)
			      

def initialize_args():
	parser = argparse.ArgumentParser(
	    description='To Monitor Interface RX Counter.',
	    epilog="""   """)
	parser.add_argument('--interfacename', '-interface', dest='interfacename',
	    help='Name of the interface \"show interface name\" command should be executed', required=True)
	parser.add_argument('--nooftimes', '-times', dest='nooftimes',
	    help='Number of times output should be displayed', required=True)
	parser.add_argument('--delay', '-delay', dest='delay',
	    help='Time delay to monitor the Interface RX Counter', required=True)
	parser.add_argument('--log', '-log', dest='log',
	    help='To write the output to file ', required=False)
	args = parser.parse_args()
	return Args(args)
    
if __name__ == '__main__':	
	params = initialize_args()
	outfile = ''
	if params.log == 'yes':
	    shostname =  json.loads(clid('show hostname'))
	    stime = json.loads(clid('show clock'))
	    filename = shostname['hostname']+'-'+stime['simple_time'].replace(' ','-')+'.log'
	    outfile = open(filename,'w')
	print_banner(params,outfile)
	nexus_cli_deploy(params,outfile)
	if params.log == 'yes':
	    print "Output has been saved in the file named ("+filename+").\n"
	
	
