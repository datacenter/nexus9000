#!/usr/bin/env python

# This script is provided by Cisco for your use for reference only as a customer courtesy.  
# It is intended to facilitate development of your own scripts and software that interoperate with Cisco switches 
# and software.  Although Cisco has made efforts to create script examples that will be effective as aids to script 
# or software development,  Cisco assumes no liability for or support obligations related to the use of this script 
# or any results obtained using or referring to this script. 
#
# verified with  NXOS image file is: bootflash:///n9000-dk9.6.1.2.I1.0.1.bin
#



import re
import sys
from cli import *
from xml.dom import minidom 

'''This script first obtains a list of all interfaces present on the system.
   The 2nd section of the script parses that file and retrieves transceiver information for each interface.
   For each entry the script also looks for CDP neighbor information.
   The scripts takes no arguments.
   '''

def nxos_help_string(args):
    # display online help (if asked for) for NX-OS' "source" command 
    # either in config mode or at the exec prompt, if users type "source <script> ?" then help_string appears
    nb_args = len(args)
    if nb_args > 1:
        help_string = "Returns a list of interfaces with transceiver information. No arguments required."
        m = re.match('__cli_script.*help', args[1])
        if m:
                # user entered "source ?" with no parameters: display script help
                if args[1] == "__cli_script_help":
                    print help_string
                    exit(0)
                # argument help
                argv = args[2:]
                # dont count last arg if it was partial help (no-space-question-mark)
                if args[1] == "__cli_script_args_help_partial":
                    argv = argv[:-1]
                nb_args = len(argv)
                # only file name provided: use man-page style help
                print "__man_page"
                print help_string
                exit(0)

def NodeAsText(node):
    # convert a XML element to a string
    try:
     nodetext=node[0].firstChild.data.strip()
     return nodetext
    except IndexError:
     return "__na__"   

def get_CDP(xml):
    neighbors = xml.getElementsByTagName("ROW_cdp_neighbor_brief_info")
    # build a dictionary of CDP neighbors with key = interface
    # the format of the dictionary is as follows:
    # neighbors = {'intf': {neighbor: 'foo', remoteport: 'x/y', model: 'bar'}}    
    cdpdict = {}
    for neighbor in neighbors:
        # intf_id format is : <intf_id>Ethernet4/1/1</intf_id>
        # however in show int brief, it is Eth4/1/1. We need to adapt Ethernet4/1/1 to Eth4/1/1.
        cdpintf  =  NodeAsText(neighbor.getElementsByTagName("intf_id"))
        cdpintf  =  cdpintf.replace("Ethernet","Eth")
        cdpneig  =  NodeAsText(neighbor.getElementsByTagName("device_id"))
        cdpport  =  NodeAsText(neighbor.getElementsByTagName("port_id"))
        cdpmodel =  NodeAsText(neighbor.getElementsByTagName("platform_id"))
        cdpipaddr = NodeAsText(neighbor.getElementsByTagName("num_mgmtaddr"))
        cdpdict[cdpintf]={'neighbor': cdpneig, \
                          'remoteport': cdpport, \
                          'model': cdpmodel,\
                          'ipaddr': cdpipaddr}
    return cdpdict


# Main
nxos_help_string(sys.argv)
raw_intf = cli('show int brief')
intf_list = raw_intf.split('\n')
cdp_neighbors = cli('show cdp neighbor | xml').replace("\n", '')

# current NXOS and eNXOS versions return NETCONF-friendly XML. We must remove the delimiter.
cdp_neighbors = cdp_neighbors.strip('\\n]]>]]>')
cdp_neighbors = cdp_neighbors + '>'

cdp_xml = minidom.parseString(cdp_neighbors)
cdp_dict = get_CDP(cdp_xml)


header1 = 'Interface  Model          Type                   Name               Part               Speed    Len   CDP Neighbor          '     
header2 = '=========================================================================================================================================='

print header1
print header2
for interface in intf_list:
    # find lines that begin with EthX/Y or EthX/Y/Z
    t= re.findall('[Ee]th\d+\/\d+ |[Ee]th\d+\/\d+\/\d+',interface)
    if len(t):
        intf = t[0].strip(' ')
        try:
            cdp = cdp_dict[intf]['neighbor'] + '@' + cdp_dict[intf]['remoteport']
        except KeyError:
            cdp = 'NA'
        tr =  cli('show int %s transceiver detail' % intf)
        if not len(re.findall('transceiver is not (present|applicable)',tr)):
            trc = cli('show int %s capabilities' % intf)
            match1 = re.search('type is\s+(.*)',tr)
            match2 = re.search('name is\s+(.*)',tr)
            match3 = re.search('Model:\s+(.*)',trc)
            match4 = re.search('part number is\s+(.*)',tr)
            match5 = re.search('Speed:\s+(.*)',trc)
            match6 = re.search('Link length supported for copper is\s+(.*)',tr)
            type   = match1.group(1)
            name   = match2.group(1).strip(' ')
            #model  = match3.group(1)
            part   = match4.group(1)
            speed  = match5.group(1)
            if match6:
               len_copper = match6.group(1)
            else:
               len_copper = 'NA'
            if match3:
		model = match3.group(1)
	    else:
		model = 'NA'  
            interface = t[0]
            str = '{0: <8} | {1: <12} | {2: <20} | {3: <16} | {4: <16} | {5: <6} | {6: <3} | {7:16}'.format(interface,model,type,name,part,speed,len_copper,cdp)
            print str

