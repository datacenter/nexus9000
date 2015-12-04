#!/usr/bin/env python
#
# tested with build n9000-dk9.6.1.2.I1.1.510.bin
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

from xml.dom import minidom
import requests

def GetiAPICookie(url, username, password):
    xml_string="<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?> \
      <ins_api>                         \
      <version>0.1</version>            \
      <type>cli_show</type>             \
      <chunk>0</chunk>                  \
      <sid>session1</sid>               \
      <input>show clock</input>         \
      <output_format>xml</output_format>\
      </ins_api>"
    try:
        r = requests.post(url, data=xml_string, auth=(username, password))
    except requests.exceptions.ConnectionError as e:
        print "Connection Error"
    else:
        return r.headers['Set-Cookie']

def ExecuteiAPICommand(url, cookie, username, password, cmd_type, cmd):
    headers = {'Cookie': cookie}

    xml_string="<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?> \
     <ins_api>                          \
     <version>0.1</version>             \
     <type>" + cmd_type + "</type>      \
     <chunk>0</chunk>                   \
     <sid>session1</sid>                \
     <input>" + cmd + "</input>         \
     <output_format>xml</output_format> \
     </ins_api>"

    try:
        r = requests.post(url, headers=headers, data=xml_string, auth=(username, password))
    except requests.exceptions.ConnectionError as e:
        print "Connection Error"
    else:
        return r.text

def GetNodeDataDom(dom,nodename):
    # given a XML document, find an element by name and return it as a string
    try:
     node=dom.getElementsByTagName(nodename)
     return (NodeAsText(node))
    except IndexError:
     return "__notFound__"

def NodeAsText(node):
    # convert a XML element to a string
    try:
     nodetext=node[0].firstChild.data.strip()
     return nodetext
    except IndexError:
     return "__na__"   

def getModules(xml):
    modules = xml.getElementsByTagName("ROW_modinfo")

    # build a dictionary of switch modules with key = slot number
    # the format of the dictionary is as follows:
    # mods = {'slot': {modtype: 'foo', ports: 'n', model: 'bar', status: 'ok'}}    
    moddict = {}
    for module in modules:
        modslot =   NodeAsText(module.getElementsByTagName("modinf"))
        modtype =   NodeAsText(module.getElementsByTagName("modtype"))
        modports =  NodeAsText(module.getElementsByTagName("ports"))
        try:
            modmodel =  NodeAsText(module.getElementsByTagName("model"))
        except:
            modmodel = '__na__'
        modstatus = NodeAsText(module.getElementsByTagName("status"))
        moddict[modslot]={'type': modtype, \
                          'ports': modports, \
                          'model': modmodel, \
                          'status': modstatus}
    return moddict

def getCDP(xml):
    neighbors = xml.getElementsByTagName("ROW_cdp_neighbor_detail_info")

    # build a dictionary of CDP neighbors with key = interface
    # the format of the dictionary is as follows:
    # neighbors = {'intf': {neighbor: 'foo', remoteport: 'x/y', model: 'bar'}}    
    cdpdict = {}
    for neighbor in neighbors:
        cdpintf  =  NodeAsText(neighbor.getElementsByTagName("intf_id"))
        cdpneig  =  NodeAsText(neighbor.getElementsByTagName("device_id"))
        cdpport  =  NodeAsText(neighbor.getElementsByTagName("port_id"))
        cdpmodel =  NodeAsText(neighbor.getElementsByTagName("platform_id"))
        cdpipaddr = NodeAsText(neighbor.getElementsByTagName("v4addr"))
        cdpdict[cdpintf]={'neighbor': cdpneig, \
                          'remoteport': cdpport, \
                          'model': cdpmodel,\
                          'ipaddr': cdpipaddr}
    return cdpdict



#################
#  MAIN MODULE  #
#################

# First things first: credentials. They should be parsed through sys.argv[] ideally ..
ip=".."
url = 'http://'+ip+'/ins/'
user=".."
password=".."

cookie=GetiAPICookie(url, user, password)

# Example 1: obtain hostname, chassis ID, NXOS version, serial number
dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, "cli_show", "show version"))
host_name=GetNodeDataDom(dom,"host_name")
chassis_id=GetNodeDataDom(dom,"chassis_id")
kickstart_ver_str=GetNodeDataDom(dom,"kickstart_ver_str")
cpu_name=GetNodeDataDom(dom,"cpu_name")
proc_board_id=GetNodeDataDom(dom,"proc_board_id")
print("System {0} is a {1} running {2}".format(host_name, chassis_id, kickstart_ver_str))
print("Its serial number is {0}".format(proc_board_id))
print("CPU is {0}\n".format(cpu_name))

# Example 2: create 10 new VLANs
for vlan in range(555, 565):
    dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, \
                                   "cli_conf", "vlan " + str(vlan) + " ; name Created_by_NXAPI"))
    if GetNodeDataDom(dom,"msg")=="Success":
        print("Config mode: Vlan %s created" % vlan)

# Example 3: create a new loopback interface
dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, "cli_conf", \
                                   "interface loopback 99 ; \
                                    ip addr 9.9.9.9/32 ; \
                                    descr Created by Python iAPI code"))
if GetNodeDataDom(dom,"msg")=="Success":
    print("Config mode: Loopback 99 created")

# Example 4: delete one of the VLANs we created
dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, \
                                   "cli_conf", "no vlan 444"))
if GetNodeDataDom(dom,"msg")=="Success":
    print("Config mode: Vlan 444 deleted")

# Example 5: iterate over "show modules"
dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, "cli_show", "show mod"))
moddict=getModules(dom)
print("\nList of modules:\n================")
for module in sorted(moddict.keys()):
    print "Slot {0}: {1}({2}),{3} ports. Status: {4}"\
          .format(module,moddict[module]['type'],\
                         moddict[module]['model'],\
                         moddict[module]['ports'],\
                         moddict[module]['status'])

# Example 6: get CDP neighbors
dom = minidom.parseString(ExecuteiAPICommand(url, cookie, user, password, "cli_show", "show cdp neighbors detail"))
cdpdict=getCDP(dom)
print("\nCDP Neighbors:\n==============")
for interface in sorted(cdpdict.keys()):
    print "Interface {0} is connected to {1} of {2}({3} @ {4})"\
          .format(interface,cdpdict[interface]['remoteport'],\
                            cdpdict[interface]['neighbor'],\
                            cdpdict[interface]['model'],\
                            cdpdict[interface]['ipaddr'])
