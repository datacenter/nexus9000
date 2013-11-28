#!/usr/bin/env python
#
#
# Copyright (C) 2013 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.
#
# v1.1
# verified with  NXOS image file is: bootflash:///n9000-dk9.6.1.2.I1.0.1.bin
#

import re
import sys
from cli import *
from xml.dom import minidom 

# color escape sequences
color_red="\x1b[31;01m"
color_green="\x1b[00;32m"
color_blue="\x1b[34;01m"
color_normal="\x1b[00m"

'''This script creates a pretty table with transceiver information and CDP neighbor detail 
   for each Ethernet interface present in the system
   '''

def nxos_help_string(args):
    # display online help (if asked for) for NX-OS' "source" command 
    # either in config mode or at the exec prompt, if users type "source <script> ?" then help_string appears
    nb_args = len(args)
    if nb_args > 1:
        help_string = color_green + "Returns a list of interfaces with transceiver information. No arguments required." + color_normal
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

def strip_netconf_trailer(x):
    # remove NETCONF's trailing delimiter
    x=x.strip('\\n]]>]]>')
    x+='>'
    return x
	 
def get_CDP(xml):
    # build a dictionary of CDP neighbors with key = interface
    # the format of the dictionary is as follows:
    # neighbors = {'intf': {neighbor: 'foo', remoteport: 'x/y', model: 'bar'}}    
	# this is what NXOS returns:
    # <ROW_cdp_neighbor_brief_info>
          # <ifindex>438829568</ifindex>
          # <device_id>ts-n6k-2(FOC1712R0RX)</device_id>
          # <intf_id>Ethernet6/2</intf_id>
          # <ttl>164</ttl>
          # <capability>router</capability>
          # <capability>switch</capability>
          # <capability>IGMP_cnd_filtering</capability>
          # <capability>Supports-STP-Dispute</capability>
          # <platform_id>N6K-C6004-96Q</platform_id>
          # <port_id>Ethernet1/2</port_id>
    # </ROW_cdp_neighbor_brief_info>
    neighbors = xml.getElementsByTagName("ROW_cdp_neighbor_brief_info")
    cdpdict = {}
    for neighbor in neighbors:
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

def get_intf(xml):
    # build a dictionary of interface details with key = interface
    # the format of the dictionary is as follows:
    # interfaces = {'interface': {iomodule: 'foo', transtype: 'foo', transname: 'foo', transpart: 'foo', transsn: 'foo', bitrate: '100', length: '5'}}    
	# this is what NXOS returns:
    # <ROW_interface>
          # <interface>Ethernet4/1/1</interface>
          # <sfp>present</sfp>
          # <type>QSFP40G-4SFP10G-CU5M</type>
          # <name>CISCO-AMPHENOL  </name>
          # <partnum>605410005       </partnum>
          # <rev>A </rev>
          # <serialnum>APF154300V9     </serialnum>
          # <nom_bitrate>10300</nom_bitrate>
          # <len_cu>5</len_cu>
          # <ciscoid>--</ciscoid>
          # <ciscoid_1>0</ciscoid_1>
    # </ROW_interface>
    interfaces = xml.getElementsByTagName("ROW_interface")
    intfdict = {}
    for intf in interfaces:
        if NodeAsText(intf.getElementsByTagName("sfp"))=="present":
            interface   =  NodeAsText(intf.getElementsByTagName("interface"))
            interface   =  interface.replace("Ethernet","Eth")
            slot        =  re.search("\d",interface)                               # find slot number            
            iomodule    =  mod_dict[slot.group(0)]['model']                        # and use it to find io_module
            transtype   =  NodeAsText(intf.getElementsByTagName("type"))
            transname   =  NodeAsText(intf.getElementsByTagName("name"))
            transpart   =  NodeAsText(intf.getElementsByTagName("partnum"))
            transsn     =  NodeAsText(intf.getElementsByTagName("serialnum"))
            bitrate     =  NodeAsText(intf.getElementsByTagName("nom_bitrate"))
            length      =  NodeAsText(intf.getElementsByTagName("len_cu"))
            intfdict[interface]={'iomodule': iomodule,\
                                 'transtype': transtype, \
                                 'transname': transname, \
                                 'transpart': transpart,\
                                 'transsn': transsn,\
				 'bitrate': bitrate,\
				 'length': length}
    return intfdict

def get_intf_capa(xml):
	# <ROW_interface>
         # <interface>Ethernet4/1/4</interface>
         # <model>N9K-X9636PQ</model>
         # <type>QSFP40G-4SFP10G-CU5M</type>
         # <speed>10000</speed>
         # <duplex>full</duplex>
         # <trunk_encap>802.1Q</trunk_encap>
         # <dce_capable>no</dce_capable>
         # <channel>yes</channel>
         # <bcast_supp>percentage(0-100)</bcast_supp>
         # <flo_ctrl>rx-(off/on/desired),tx-(off/on/desired)</flo_ctrl>
         # <rate_mode>dedicated</rate_mode>
         # <port_mode>Routed,Switched</port_mode>
         # <qos_scheduling>rx-(none),tx-(4q)</qos_scheduling>
         # <cos_rewrite>yes</cos_rewrite>
         # <tos_rewrite>yes</tos_rewrite>
         # <span>yes</span>
         # <udld>yes</udld>
         # <mdix>no</mdix>
         # <tdr>no</tdr>
         # <lnk_debounce>yes</lnk_debounce>
         # <lnk_debounce_time>yes</lnk_debounce_time>
         # <fex_fabric>yes</fex_fabric>
         # <dot1q_tunnel>yes</dot1q_tunnel>
         # <pvlan_trunk_mode>yes</pvlan_trunk_mode>
         # <port_group_members>4</port_group_members>
         # <eee_capable>no</eee_capable>
         # <pfc_capable>yes</pfc_capable>
        # </ROW_interface>
    interfaces = xml.getElementsByTagName("ROW_interface")
    capadict = {}
    for intf in interfaces:
        interface   =  NodeAsText(intf.getElementsByTagName("interface"))
        interface   =  interface.replace("Ethernet","Eth")
        speed       =  NodeAsText(intf.getElementsByTagName("speed"))
        capadict[interface]={'speed': speed}
    return capadict
	
def get_modules(xml):
    # build a dictionary of i/o modules details with key = slot_number
    # the format of the dictionary is as follows:
    # modules = {'slot_number': {model: 'foo'}}    
	# this is what NXOS returns:
	# <ROW_modinfo>
         # <modinf>6</modinf>
         # <ports>36</ports>
         # <modtype>36p 40G Ethernet Module</modtype>
         # <model>N9K-X9636PQ</model>
         # <status>ok</status>
    # </ROW_modinfo>
    modules = xml.getElementsByTagName("ROW_modinfo")
    moddict = {}
    for mod in modules:
        slot    =  NodeAsText(mod.getElementsByTagName("modinf"))
        model   =  NodeAsText(mod.getElementsByTagName("model"))
        moddict[slot]={'model': model}
    return moddict
	
# Main
nxos_help_string(sys.argv)
intf_list     = cli('show int transceiver detail | xml').replace("\n", '')
cdp_neighbors = cli('show cdp neighbor | xml').replace("\n", '')
io_modules    = cli('show module | xml').replace("\n", '')
intf_capa     = cli('show int capa | xml').replace("\n", '')

# current NXOS and eNXOS versions return NETCONF-friendly XML. We must remove the delimiter.
cdp_neighbors = strip_netconf_trailer(cdp_neighbors)
intf_list     = strip_netconf_trailer(intf_list)
io_modules    = strip_netconf_trailer(io_modules)
intf_capa     = strip_netconf_trailer(intf_capa)

cdp_xml   = minidom.parseString(cdp_neighbors)
cdp_dict  = get_CDP(cdp_xml)
mod_xml   = minidom.parseString(io_modules)
mod_dict  = get_modules(mod_xml)
intf_xml  = minidom.parseString(intf_list)
intf_dict = get_intf(intf_xml)
capa_xml  = minidom.parseString(intf_capa)
capa_dict = get_intf_capa(capa_xml)

header1 = 'Interface  Model          Type                   Name               Part               Speed    Len      CDP Neighbor          '     
header2 = '=========================================================================================================================================='

print color_green+header1
print header2+color_normal

for interface in sorted(intf_dict):
    model = intf_dict[interface]['iomodule']
    type  = intf_dict[interface]['transtype']
    name  = intf_dict[interface]['transname']
    part  = intf_dict[interface]['transpart']
    speed = capa_dict[interface]['speed']
    lencu = intf_dict[interface]['length']
    try:
        cdp = cdp_dict[interface]['neighbor'] + '@' + cdp_dict[interface]['remoteport']
    except KeyError:
            cdp = '__na__'
    str = '{0: <8} | {1: <12} | {2: <20} | {3: <16} | {4: <16} | {5: <6} | {6: <6} | {7:16}'.format(interface,model,type,name,part,speed,lencu,cdp)
    print color_blue+str
print color_normal