"""
 Cisco Nexus 9000 Switch On-Box script for displaying given Switch details.
"""

import os,sys,re
import json
import argparse
import time
from cli import *

"""
Class to fetch Switch details
"""

class Args(object):

    def __init__(self, args):
        self.ip = args.ip 
        self.log = args.log		
        
def print_banner(params, outfile):

    msg = "*"*95
    msg += '\n    Cisco Nexus 9000 Switch On-Box script for displaying given Switch details.\n'	
    msg += '\nDeveloped By: OneCloud Consulting\n'	
    msg += 'Please contact info@1-cloud.net for any queries.\n\n'	
    msg += "*"*95
    msg += "\n"
    print msg
    if params.log == 'yes':
	    outfile.write(msg)
	
def nexus_cli_deploy(params, outfile):		
	
	switch_data = json.loads(clid('show ip route '+params.ip))
	try:
		interface_data = switch_data['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']['TABLE_path']['ROW_path'][0]
		if 'ifname' not in interface_data:
			msg = "There is NO route for this IP address\n"
		else:
			switch_intdata = json.loads(clid('show cdp neighbors interface '+interface_data['ifname']+' detail'))
			msg = "Device ID: "+switch_intdata['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']['device_id']+"\n"
			msg += "System name: "+switch_intdata['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']['sysname']+"\n"
			msg += "Platform: "+switch_intdata['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']['platform_id']+"\n"
			msg += "Version: "+switch_intdata['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']['version']+"\n"
			msg += "Management Address: "+switch_intdata['TABLE_cdp_neighbor_detail_info']['ROW_cdp_neighbor_detail_info']['v4mgmtaddr']+"\n"
			msg += "\n"
	except KeyError, e:
		msg = "There is NO route for this IP address\n"
	print msg
	if params.log == 'yes':
		outfile.write(msg)
		
def initialize_args():
	parser = argparse.ArgumentParser(
	    description='To Fetch Switch Details.',
	    epilog="""   """)
	parser.add_argument('--ip', '-ip', dest='ip',
	    help='Please enter the Switch IP', required=True)
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
	
