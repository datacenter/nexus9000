# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
#$Id: eor_utils.py,v 1.427 2013/06/24 23:56:03 venksrin Exp $ 
#ident $Source: /cvsroot/eor/systest/lib/eor_utils.py,v $ $Revision: 1.427 $

# Best Pratices for get() functions:
# 1. Use class rex as much as possible for standard regular expressions
# 2. Use underscore in keys wherever white-space appears in the output header
# 3. Add author name, description of function, sample usage examples and return value
# 4. Use python documentation format for #3 above, so that the documentation for all the functions can be pulled out easily

from nxapi_utils import NXAPITransport

import re                                                       
import collections                               
import string
import subprocess
import shlex
import sys, socket
import datetime
import time

MASKS=['0.0.0.0','128.0.0.0','192.0.0.0','224.0.0.0','240.0.0.0','248.0.0.0','252.0.0.0','254.0.0.0','255.0.0.0','255.128.0.0','255.192.0.0','255.224.0.0','255.240.0.0','255.248.0.0','255.252.0.0', '255.254.0.0', '255.255.0.0', '255.255.128.0', '255.255.192.0', '255.255.224.0', '255.255.240.0', '255.255.248.0', '255.255.252.0', '255.255.254.0', '255.255.255.0', '255.255.255.128', '255.255.255.192', '255.255.255.224', '255.255.255.240', '255.255.255.248', '255.255.255.252', '255.255.255.254', '255.255.255.255']

####################################################################
# Block that hijack on-box cli and convert into NX-API calls
####################################################################
def runNXAPIConf(cmd):
    output,code,msg = NXAPITransport.send_cmd_int(cmd, "cli_conf")
    return output,msg,code

def runNXAPIShow(cmd):
    xml_index = cmd.find("| xml")
    if xml_index == -1:
        output,code,msg = NXAPITransport.send_cmd_int(cmd, "cli_show_ascii")
    else:
        cmd = cmd[:xml_index]
        output,code,msg = NXAPITransport.send_cmd_int(cmd, "cli_show")
    return output

def runVshCmdEx(cmd, _shell = False, _stdout = None):                                
   output,error,status = runNXAPIConf(cmd)
   return output,error,status 

def cli_ex(cmd):
    if "config" in cmd:
      return runNXAPIConf(cmd)
    else:
      return runNXAPIShow(cmd)
####################################################################
    
class rex:
   INTERFACE_TYPE="[Ff]ast[Ee]thernet|[Ff][Ee]th|[Gg]igabit[Ee]thernet|[Gg]ig[Ee]|[Ee]thernet|[Ee]th|[Tt]unnel ?|[Ll]oopback ?|[Pp]ort-channel ?|[Oo]verlay ?|[Nn]ull|[Mm]gmt|[Vv]lan ?|[Pp]o ?|[Ll]o ?|[Oo]vl ?|[Vv][Ll]|[Rr]epl|[Rr]eplicator|[Ff]as|[Ss]up-eth"
   INTERFACE_NUMBER="[0-9]+/[0-9]+/[0-9]+|[0-9]+/[0-9]+|[0-9]+/[0-9]+\.[0-9]+|[0-9]+\.[0-9]+|[0-9]+|[0-9]+/[0-9]+/[0-9]+"
#   INTERFACE_NAME="(?:{0})(?:{1})|[Nn]ull".format(INTERFACE_TYPE,INTERFACE_NUMBER)

   INTERFACE_NAME='(?:(?:{0})(?:{1})|(?:[Nn]ull))'.format(INTERFACE_TYPE,INTERFACE_NUMBER)
   INTERFACE_RANGE='(?:(?:{0}-[0-9]+|{0}-{0}|{0}),?)+'.format(INTERFACE_NAME)
   BCM_FP_INTERFACE='([Xx]e([0-9]+))'
   BCM_FP_INTERFACE_RANGE='[Xx]e([0-9]+)-[Xx]e([0-9]+)'

   PHYSICAL_INTERFACE_TYPE="[Ff]ast[Ee]thernet|[Ff][Ee]th|[Gg]igabit[Ee]thernet|[Gg]ig[Ee]|[Gg]i|[Ee]thernet|[Ee]th"
   PHYSICAL_INTERFACE_NUMBER="[0-9]+/[0-9]+/[0-9]+|[0-9]+/[0-9]+|[0-9]+"
   PHYSICAL_INTERFACE_NAME="(?:{0})(?:{1})".format(PHYSICAL_INTERFACE_TYPE,PHYSICAL_INTERFACE_NUMBER)

   PHYSICAL_INTERFACE_RANGE='(?:(?:{0}-[0-9]+|{0}-{0}|{0}),?)+'.format(PHYSICAL_INTERFACE_NAME)

   DEVICE_TYPE='EOR|sTOR|N7K|N5K|N3K|itgen|fanout|UNKNOWN|NA'
   FEX_MODEL='N2148T|N2232P|N2232TM-E|N2248TP-E|N2248T|NB22FJ|NB22HP'
   FEX_INTERFACE_TYPE='{0}[0-9][0-9][0-9]/[0-9]+/[0-9]+'.format(PHYSICAL_INTERFACE_TYPE)
   SWITCH_NAME = '[0-9A-Za-z_-]+'
   #VLAN_RANGE  = '[0-9]+(?:\-[0-9]+)?'

   HEX="[0-9a-fA-F]+"
   HEX_VAL="[x0-9a-fA-F]+"
   MACDELIMITER="[\.:\-]"
   # Following will match the following combinations
   #  Aa.Bb.Cc.Dd.Ee.Ff
   #  Aa-Bb-Cc-Dd-Ee-Ff
   #  Aa:Bb:Cc:Dd:Ee:Ff
   #  AaBb.CcDd.EeFf
   #  AaBb-CcDd-EeFf
   #  AaBb:CcDd:EeFf
   MACADDR=HEX+HEX+MACDELIMITER+HEX+HEX+MACDELIMITER+HEX+HEX+MACDELIMITER+HEX+HEX+MACDELIMITER+HEX+HEX+MACDELIMITER+HEX+HEX+"|"+HEX+HEX+HEX+HEX+MACDELIMITER+HEX+HEX+HEX+HEX+MACDELIMITER+HEX+HEX+HEX+HEX
   IPv4_ADDR="[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"
   IPv6_ADDR="[0-9A-Fa-f]+:[0-9A-Fa-f:]+"

   LINK_LOCAL_IPv6_ADDR="fe80::[0-9A-Fa-f]+:[0-9A-Fa-f]+:[0-9A-Fa-f]+:[0-9A-Fa-f]+"
   IP_ADDRESS="(?:(?:{0})|(?:{1}))".format(IPv4_ADDR,IPv6_ADDR)
   NETADDR ='{0}/[0-9]+'.format(IPv4_ADDR)
   NUM="[0-9]+"
   BOOL="[01]"
   DECIMAL_NUM="[0-9\.]+"
   ALPHA="[a-zA-Z]+"
   ALPHAUPPER="[A-Z]+"
   ALPHALOWER="[a-z]+"
   ALPHASPECIAL="[a-zA-Z_\-\.#/]+"
   ALPHANUM="[a-zA-Z0-9]+"
   ALPHANUMSPECIAL="[a-zA-Z0-9\-\._/]+"
   SYSMGR_SERVICE_NAME = "[a-zA-Z0-9\-\._ ]+"
   VRF_NAME="[a-zA-Z0-9_\-#]+"
   ALL="?:[.\s]+"
   #
   # Number and time formats
   #
   VLAN_RANGE='(?:(?:{0}-[0-9]+|{0}-{0}|{0}),?)+'.format(NUM)

   DATE = '[0-9]+\-[0-9]+\-[0-9]+'
   U_TIME="[0-9]+\.[0-9]+"
   CLOCK_TIME="[0-9]+[0-9]+:[0-9]+[0-9]+:[0-9]+[0-9]+"
   HH_MM_SS="[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}"
   TIME="(?:$U_TIME|$CLOCK_TIME)"
   MONTH="Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
   YEAR="[12]+[0-9][0-9][0-9]"
   UPTIME="(?:\d+[dwmy]\d+[hdwm]|\d+:\d+:\d+|\d+\.\d+)"
   XPTIME="(?:\d+:\d+:\d+|\d+\.\d+|never)"

   LC_STATUS='(?:pwr-?denied|err-?pwd-?dn|pwr-?cycle?d|upgrading|powered-?up|powered-?dn|failure|initializing|testing|ok)'
   LC_MODEL='(?:N7K-F2-?48X[PT]-?\d+[E]*| +|Cortina-Test-LC|N9k-X9636PQ)'
   FC_MODEL='(?:N7K-C[0-9]+-FAB-?\d+|N/A| +)'
   LC_MODULE_TYPE='(?:[0-9]+/[0-9]+ Gbps (?:BASE-T )?Ethernet Module|Cortina-Test-LC|Snowbird|Seymour)' 
   FC_MODULE_TYPE='(?:Fabric Module(?: [0-9]+)?|Sierra|Shasta)'
   VLAN_STATUS='active|suspended|act.lshut'
   
   #Verify_list defined for stimuli classes
   VERIFY_LIST=['none','all','traffic','l2_unicast_pi','l3_unicast_pi','l2_multicast_pi','l3_multicast_pi','l2_unicast_pd','l3_unicast_pd','l2_multicast_pd','l3_multicast_pd','system','exception','vpc_consistency']
   TRIGGER_VERIFY_LIST=['traffic','none','all']


# To be depreceated, use strTolist instead
# Usages strtolist('1,2,3')
#        strtolist('1 2 3')
#        strtolist('1, 2, 3')
# All three will return list of ['1',2,'3']
def strtolist(inputstr,retainint=False):
     inputstr=str(inputstr)
     inputstr=inputstr.strip("[]")
     splitbycomma=inputstr.split(",")
     splitbyspace=inputstr.split()
     if len(splitbycomma) >= 2:
         returnlist=[]
         for elem in splitbycomma:
             elem=elem.strip(" '")
             elem=elem.strip('"')
             if elem.isdigit() and retainint:
                 returnlist.append(int(elem))
             else:
                 returnlist.append(elem)
         return returnlist
     returnlist=[]
     for elem in splitbyspace:
         elem=elem.strip(" '")
         elem=elem.strip('"')
         if elem.isdigit() and retainint:
             returnlist.append(int(elem))
         else:
             returnlist.append(elem)
     return returnlist

def normalizeInterfaceName(log, interface):
     in_type=type(interface)
     pattern1='[Ee]thernet|[Ee]th|[Ee]t'
     pattern2='[Vv]lan|[Vv]l'
     pattern3='[Pp]ort-channel|[Pp]ortchannel|[Pp]o'
     pattern4='[Ll]oopback|[Ll]oop-back|[Ll]o'
     if (in_type == str):
         interface=re.sub(r'(?:{0})((?:{1}))'.format(pattern1,rex.INTERFACE_NUMBER),r'Eth\1',interface)
         interface=re.sub(r'(?:{0})((?:{1}))'.format(pattern2,rex.INTERFACE_NUMBER),r'Vlan\1',interface)
         interface=re.sub(r'(?:{0})((?:{1}))'.format(pattern3,rex.INTERFACE_NUMBER),r'Po\1',interface)
         interface=re.sub(r'(?:{0})((?:{1}))'.format(pattern4,rex.INTERFACE_NUMBER),r'Lo\1',interface)
     if (in_type == list):
         for int in interface:
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern1,rex.INTERFACE_NUMBER),r'Eth\1',int)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern2,rex.INTERFACE_NUMBER),r'Vlan\1',tmp)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern3,rex.INTERFACE_NUMBER),r'Po\1',tmp)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern4,rex.INTERFACE_NUMBER),r'Lo\1',tmp)
             interface[interface.index(int)]=tmp
     if (in_type == tuple):
         int_list=list(interface)
         for int in int_list:
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern1,rex.INTERFACE_NUMBER),r'Eth\1',int)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern2,rex.INTERFACE_NUMBER),r'Vlan\1',tmp)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern3,rex.INTERFACE_NUMBER),r'Po\1',tmp)
             tmp=re.sub(r'(?:{0})((?:{1}))'.format(pattern4,rex.INTERFACE_NUMBER),r'Lo\1',tmp)
             int_list[int_list.index(int)]=tmp
         interface=tuple(int_list)
     if (in_type == dict):
         dct={}
         for key in interface.keys():
             int=re.sub(r'(?:{0})((?:{1}))'.format(pattern1,rex.INTERFACE_NUMBER),r'Eth\1',key)
             int=re.sub(r'(?:{0})((?:{1}))'.format(pattern2,rex.INTERFACE_NUMBER),r'Vlan\1',int)
             int=re.sub(r'(?:{0})((?:{1}))'.format(pattern3,rex.INTERFACE_NUMBER),r'Po\1',int)
             int=re.sub(r'(?:{0})((?:{1}))'.format(pattern4,rex.INTERFACE_NUMBER),r'Lo\1',int)
             tmp={int:interface[key]}
             dct.update(tmp)
         interface=dct

     return interface
def convertListToDict(table,columns=[],keys=None,keytype="tuple"):

    # Returns dictionary based on given list & columns
    # If it is a list, each column is a key
    # If it is a list of lists, then first level keys are passed keys argument
    # and columns is second level key

    returnDict = collections.OrderedDict()
    if keys: 
        keyIndexes = []
        if "split" in dir(keys):
            keys=keys.split()
        for key in keys:
            keyIndexes.append(columns.index(key))

        valueIndex=-1
        if len(columns) - len(keys) == 1:
            for i in range(len(columns)):
                if not i in keyIndexes:
                   valueIndex=i
                   break

        for row in table:
            key=""
            keyitems=[]
            initial=True
            for keyIndex in keyIndexes:
               interface=""
               temp=re.match(rex.INTERFACE_NAME,row[keyIndex])
               if temp and temp.group(0) == row[keyIndex]:
                   interface=normalizeInterfaceName("",row[keyIndex]) 
               if initial:
                   if interface == "": 
                       key = key + row[keyIndex]
                   else:
                       key = key + interface
                   initial=False
               else:
                   if interface == "": 
                       key = key + " " + row[keyIndex]
                   else:
                       key = key + " " + interface
               if interface == "":
                   keyitems.append(row[keyIndex])
               else:
                   keyitems.append(interface)
            if keytype == "tuple" and len(keys) > 1:
                key=tuple(keyitems)
            returnDict[key] = collections.OrderedDict()
            if valueIndex == -1:
                for i in range(len(columns)):
                    if not i in keyIndexes:
                       temp=re.match(rex.INTERFACE_NAME,row[i].strip())
                       if temp and temp.group(0) == row[i].strip():
                          returnDict[key][columns[i]]=normalizeInterfaceName("",row[i].strip()) 
                       else:
                           returnDict[key][columns[i]] = row[i].strip()
            else:
               temp=re.match(rex.INTERFACE_NAME,row[valueIndex].strip())
               if temp and temp.group(0) == row[valueIndex].strip():
                   returnDict[key]=normalizeInterfaceName("",row[valueIndex].strip()) 
               else:
                   returnDict[key] = row[valueIndex]
    else:
        #Single level dictionary need to handle 6 different use cases
        #eor_utils.convertListToDict(['x','y','z'],['a','b','c'])
        #eor_utils.convertListToDict([],['a','b','c'])
        #eor_utils.convertListToDict(['x','y'],['a','b','c'])
        #eor_utils.convertListToDict([('x','y','z')],['a','b','c'])
        #eor_utils.convertListToDict([('x','y'),('c','d')],['a','b'])
        #eor_utils.convertListToDict([('x','y'),('c','d')])
        if len(table):
            if len(columns) == len(table) and not re.search('tuple',str(type(table[0]))):
                for key in columns:
                    temp=re.match(rex.INTERFACE_NAME,table[columns.index(key)])
                    if temp and temp.group(0) == table[columns.index(key)]:
                        returnDict[key]=normalizeInterfaceName("",table[columns.index(key)]) 
                    else:
                        returnDict[key]=table[columns.index(key)]
            elif len(table) == 1 and len(table[0]) == len(columns) and re.search('tuple',str(type(table[0]))):
                for key in columns:
                    temp=re.match(rex.INTERFACE_NAME,table[0][columns.index(key)])
                    if temp and temp.group(0) == table[0][columns.index(key)]:
                        returnDict[key]=normalizeInterfaceName("",table[0][columns.index(key)]) 
                    else:
                        returnDict[key]=table[0][columns.index(key)]
            elif (len(columns) == 2 or len(columns) == 0)and re.search('tuple',str(type(table[0]))):
                for row in table:
                    if len(row) == 2:
                       temp=re.match(rex.INTERFACE_NAME,row[1])
                       if temp and temp.group(0) == row[1]:
                            returnDict[row[0]]=normalizeInterfaceName("",row[1]) 
                       else:
                            returnDict[row[0]]=row[1]
                    else:
                       return collections.OrderedDict()
    return returnDict

def getUnwrappedBuffer(buffer,delimiter=" "):

    # Returns a string
    # If output has wrapped lines as follows (port-channel summary)
    # "21    Po21(SU)    Eth      NONE      Eth2/11(P)   Eth2/12(D)
    #  22    Po22(SU)    Eth      NONE      Eth1/1(P)    Eth1/2(P)    Eth1/3(P)
    #                                       Eth1/4(P)
    #  101   Po101(SD)   Eth      NONE      Eth2/1(D)    Eth2/2(D)"
    # This converts to
    # "21    Po21(SU)    Eth      NONE      Eth2/11(P)   Eth2/12(D)
    #  22    Po22(SU)    Eth      NONE      Eth1/1(P)    Eth1/2(P)    Eth1/3(P) Eth1/4(P)
    #  101   Po101(SD)   Eth      NONE      Eth2/1(D)    Eth2/2(D)"
    #
    # This helps to write get procedures with everyoutput being a single line 
    # and makes regular expressions seamless independent of wrapped output

    previousline=""
    lines=[]
    returnbuffer = ""
    buffer=re.sub("\r","",buffer)
    for line in buffer.split("\n"):
        wrappedline=re.findall("^[ \t]+(.*)",line,flags=re.I)
        if len(wrappedline) > 0:
           previousline = previousline + delimiter + re.sub("\r\n","",wrappedline[0])
        else:
           if (previousline != ""):
               returnbuffer = returnbuffer + previousline + "\n"
           previousline=re.sub("[\r\n]+","",line)
    if (previousline != ""):
          returnbuffer = returnbuffer + previousline + "\n"
    return returnbuffer




def getVlanDict(vlan):

    cmd = "show vlan id " + vlan 
    showoutput=cli_ex(cmd)

    vlanmemberlist=re.findall("("+rex.NUM+")[ \t]+("+rex.ALPHANUM+")[ \t]+("+rex.VLAN_STATUS+")[ \t]+(.*)",getUnwrappedBuffer(showoutput,", "),flags=re.I|re.M)
    vlanmemberdict=convertListToDict(vlanmemberlist,['VLAN','Name','Status','Ports'],['VLAN'])
    return vlanmemberdict

 
"""This scrpit should not contain any thing other than enums"""
class IfType():
       Ethernet = 1
       PortChannel = 2
       Internal = 3
       Cpu = 4


def replace_output(_lines, _find_word, _replace_word):
    hw_name = _find_word
    new_lines = []

    for line in _lines:
        x = re.sub(r'\b%s\b'%(hw_name), _replace_word, line)
        new_lines.append(x)

    return new_lines

class createHwTableObject(object):

    """ Class to parse the broadcom table outputs and convert to dictionary format. Expects the
    input as 'Index: <Row>' where the <Row> is in key value pairs separated by commas"""

    def __init__( self, bcm_cmd_dump ):

       import re

       self.table=collections.OrderedDict()

       table_rows=bcm_cmd_dump.split('\n')
       for row in table_rows:
          if "d chg" in row:
              continue
          if ":" not in row:
                 continue
          if "Private image version" in row:
                 continue

          (row_key, row_value)=row.split(': ')
          (row_key, row_value)=row.split(': ')
          value_row=row_value.rstrip('\r').lstrip('<').rstrip('>')
          self.table[row_key]=collections.OrderedDict()
          for data_params in value_row.split(','):
             if len(data_params) == 0:
                 continue

             (data_key,data_value)=data_params.split('=')
             self.table[row_key][data_key]=data_value
       #print('Table Data', self.table )



def getSpanningTreeVlanPortStateDict(vlan):
    cmd = "show spanning-tree " + vlan
    showoutput=cli_ex(cmd)
    stplist=re.findall("^([^ \t]+)[ \s]+([^ \t]+)[ \s]+([A-Za-z]+)[ \s]+([0-9]+)[ \s]+\
    ([^ \t]+)[ \s]+([^ \t]+)[ \s\r\n]+",showoutput,flags=re.I|re.M)
    if stplist:
        # if vlan port state is found
        stpdict=convertListToDict(stplist,['vlan','role','state','cost','prio.nbr','type'])
        log.info(" STP state for " + \
        parserutils_lib.argsToCommandOptions(args,arggrammar,log,"str") + " is : " + str(stpdict))
        return stpdict  

def getShowSpanningTreeDict( vlan ):

  
    show_stp_dict=collections.OrderedDict()
 

    # Define the Regexp Patterns to Parse ..

    root_params_pat_non_root='\s+Root ID\s+Priority\s+([0-9]+)\r\n\s+Address\s+({0})\r\n\s+Cost\s+([0-9]+)\r\nPort\s+([0-9]+)\s+\(([a-zA-Z0-9\-]+)\)\r\n\s+Hello Time\s+([0-9]+)\s+sec\s+Max\s+Age\s+([0-9]+)\s+sec\s+Forward\s+Delay\s+([0-9]+)\s+sec\r\n'.format(rex.MACADDR)
    root_params_pat_root='\s+Root ID\s+Priority\s+([0-9]+)\r\n\s+Address\s+({0})\r\n\s+This bridge is the root\r\n\s+Hello Time\s+([0-9]+)\s+sec\s+Max\s+Age\s+([0-9]+)\s+sec\s+Forward\s+Delay\s+([0-9]+)\s+sec\r\n'.format(rex.MACADDR)
    bridge_params_pat='\s+Bridge ID\s+Priority\s+([0-9]+)\s+\(priority\s+([0-9]+)\s+sys-id-ext ([0-9]+)\)\r\n\s+Address\s+({0})\r\n\s+Hello\s+Time\s+([0-9]+)\s+sec\s+Max\s+Age\s+([0-9+)\s+sec\s+Forward Delay\s+([0-9]+) sec\r\n'.format(rex.MACADDR)
    #interface_params_pat='-------\r\n({0})\s+([a-zA-Z]+)\s+([A-Z]+)\s+([0-9]+)\s+([0-9]+).([0-9]+)\s+([\(\)a-zA-Z0-9\s]+)\r'.format(rex.INTERFACE_NAME)
    interface_params_pat='({0})\s+([a-zA-Z]+)\s+([A-Z]+)[\*\s]+([0-9]+)\s+([0-9]+).([0-9]+)\s+'.format(rex.INTERFACE_NAME)


    # Build the command to be executed based on the arguments passed ..
    cmd = 'show spanning-tree '

    cmd = cmd + 'vlan ' + str(vlan)


    show_stp=cli_ex(cmd)

    # Split the output of STP based on VLAN
    show_stp_vlan_split=show_stp.split('VLAN')


    # Iterate over every VLAN block and build the show_stp_dict
    for stp_vlan in show_stp_vlan_split:

      if re.search( '^([0-9]+)', stp_vlan ):

         #removed backslash r
         match=re.search( '^([0-9]+)\n\s+Spanning tree enabled protocol ([a-z]+)', stp_vlan, re.I )
         vlan_id = int(match.group(1))
         stp_mode = match.group(2)
         show_stp_dict[vlan_id]={}
         show_stp_dict[vlan_id]['stp_mode']=stp_mode
         

         if re.search( root_params_pat_root, stp_vlan, re.I ):
             root_info=re.findall( root_params_pat_root, stp_vlan, re.I )
             show_stp_dict[vlan_id]['root_info']=convertListToDict( root_info, ['Priority','Address', \
                 'Hello Time','Max Age','Forward Delay'], ['Priority','Address'])
             show_stp_dict[vlan_id]['root']=True
         else:
             root_info=re.findall( root_params_pat_non_root, stp_vlan, re.I )
             show_stp_dict[vlan_id]['root_info']=convertListToDict( root_info, ['Priority','Address','Cost', \
                 'Port','Hello Time','Max Age','Forward Delay'], ['Priority','Address','Cost', 'Port'])
             show_stp_dict[vlan_id]['root']=False

         bridge_info=re.findall( bridge_params_pat, stp_vlan, re.I )
         show_stp_dict[vlan_id]['bridge_info']=convertListToDict( root_info, ['Priority','Address', \
                'Hello Time','Max Age','Forward Delay'], ['Priority','Address'])

         intf_info=re.findall( interface_params_pat, stp_vlan, re.I )
         show_stp_dict[vlan_id]['Interface_info']=convertListToDict( intf_info, [ 'Interface', 'Role', 'Status', \
                'Cost', 'Prio', 'Nbr' ] , [ 'Interface' ] )

    # Split the output of STP based on MST 
    show_stp_mst_split=show_stp.split('MST')

    for mst_id in show_stp_mst_split:                                                                            
                                                                                                                  
      if re.search( '^([0-9]+)', mst_id):                                                                         
                                                                                                                  
         #removed backslash r                                                                                              
         match=re.search( '^([0-9]+)\n\s+Spanning tree enabled protocol ([a-z]+)', mst_id, re.I )                 
         mst = vlan                                                                        
         stp_mode = match.group(2)                                                                                
         show_stp_dict[mst]={}                                                                                    
         show_stp_dict[mst]['stp_mode']=stp_mode                                                              
                                                                                                              
                                                                                                              
         if re.search( root_params_pat_root, mst_id, re.I ):                                                  
             root_info=re.findall( root_params_pat_root, mst_id, re.I )                                       
             show_stp_dict[mst]['root_info']=convertListToDict( root_info, ['Priority','Address', \
                 'Hello Time','Max Age','Forward Delay'], ['Priority','Address'])                             
             show_stp_dict[mst]['root']=True                
         else:                                                                                                    
             root_info=re.findall( root_params_pat_non_root, mst_id, re.I )                                       
             show_stp_dict[mst]['root_info']=convertListToDict( root_info, ['Priority','Address','Cost', \
                 'Port','Hello Time','Max Age','Forward Delay'], ['Priority','Address','Cost', 'Port'])           
             show_stp_dict[mst]['root']=False                                                             
                                                                                                                  
         bridge_info=re.findall( bridge_params_pat, mst_id, re.I )                                                
         show_stp_dict[mst]['bridge_info']=convertListToDict( root_info, ['Priority','Address', \
                'Hello Time','Max Age','Forward Delay'], ['Priority','Address'])                              
                                                                                                              
         intf_info=re.findall( interface_params_pat, mst_id, re.I )                                           
         show_stp_dict[mst]['Interface_info']=convertListToDict( intf_info, [ 'Interface', 'Role', 'Status', \
                'Cost', 'Prio', 'Nbr' ] , [ 'Interface' ] )               
    return show_stp_dict
    
def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        # left col
        print >> out, row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        for i in range(1, len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out 
 

def validateIP(ip):
    try:
       socket.inet_aton(ip)
       return 0
    except socket.error:
       return 1

def convertIP(ip):
    hexIP = []
    [hexIP.append(hex(int(x))[2:].zfill(2)) for x in ip.split('.')]
    hexIP = "0x" + "".join(hexIP)
    return hexIP

class createEventHistoryTableObject(object):

    """ Class to parse the event history outputs and convert to dictionary format. Expects the
    input as 'Index: <Row>' where the <Row> is in key value pairs separated by commas"""

    def __init__( self, event_history_dump ):

       import re
       time_format = "at %f usecs after %a %b %d %H:%M:%S %Y"

       self.table=[]

       table_rows=event_history_dump.split('\n')
       new = {}
       esq_req_rsp = {}
       esqs = []
       esq_start = []
       req_rsp = True
       for row in table_rows:
          if "FSM" in row:
              continue
          if ":" not in row:
                 continue

          if "Previous state:" in row:
              if req_rsp == False:
                  esq_start.append(esq_req_rsp)
                  req_rsp = True
                  esq_req_rsp = {}

              if len(esq_start) > 0:
                  esqs.append(esq_start)
                  esq_start = []

              continue
          if "Triggered event:" in row:
              if req_rsp == False:
                  esq_start.append(esq_req_rsp)
                  req_rsp = True
                  esq_req_rsp = {}

              if len(esq_start) > 0:
                  esqs.append(esq_start)
                  esq_start = []

              continue
          if "Next state:" in row:
              if req_rsp == False:
                  esq_start.append(esq_req_rsp)
                  req_rsp = True
                  esq_req_rsp = {}

              if len(esq_start) > 0:
                  esqs.append(esq_start)
                  esq_start = []

              continue


          if "ESQ_START" in row:
              if req_rsp == False:
                  esq_start.append(esq_req_rsp)
                  req_rsp = True
                  esq_req_rsp = {}

              if len(esq_start) > 0:
                  esqs.append(esq_start)

              esq_start = []
              continue

          if "ESQ_REQ" in row or "ESQ_RSP" in row:
              old = esq_req_rsp
              esq_req_rsp = {}
              if len(old) > 0:
                  esq_start.append(old)
                  req_rsp = True

          if "usecs after" in row:
              y = row.split(',')[1].strip()
              t = datetime.datetime.strptime(y, time_format)
              esq_req_rsp['TIME'] = t
              esq_req_rsp['TIME_STRING'] = row

          kvpairs = row.split(',')
          for val in kvpairs:
              
              x = val.strip(' ').strip('\r').split(':')
              if len(x) != 2:
                  continue

              (tk, tv)=val.split(':')
              row_key = tk.strip(' ')
              row_value = tv.strip(' ')
              req_rsp = False
              esq_req_rsp[row_key]=row_value

       if req_rsp == False:
           esq_start.append(esq_req_rsp)
           esqs.append(esq_start)

       self.table = esqs
       
