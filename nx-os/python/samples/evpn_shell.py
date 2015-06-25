#!/usr/bin/python
#
#     VXLAN EVPN Shell
#     v0.3
#
#     - v0.3:
#       * Added the command "ip forward" on each SVI for the L3 VNI
#       * Added the multicast address information to the "show_vlans" command
#       * Change log defaults to NOT logging
#     - v0.2:
#       * Added per switch creation/deletion
#       * Debug log
#       * getTenants bug fixed
#       * Consolidated switch list (instead of one for leafs and another one for spines)
#
#     Jose Moreno (josemor@cisco.com)
#       April 2015
#
#     This program provides a CLI to manage a VXLAN EVPN
#       environment distributed on multiple switches. It
#       helps creating tenants and VLANs.
#     It is built on the API of NXOS (NX-API) and
#       the python modules on it (nxapi_utils).
#
#     This is NOT thought to be run in a production
#       network, there are some things that would need
#       to be improved (for example password encryption).
#
#
import sys
import cmd2
import json
import datetime
# This file is supposed to be located in the remote_client folder
#  after unpacking the N9K Python SDK modules
#  (https://developer.cisco.com/fileMedia/download/0eb10f7e-b1ee-432a-9bef-680cb3ced417)
sys.path.append("./cisco")
sys.path.append("./utils")
from nxapi_utils import NXAPITransport 
#Not using this library any more
#from cisco.interface import Interface


############################
# Multi-switch class
############################
class multicli:
  switches=[]
  debug = False
  debugtofile = False
  debugfilename = "evpn.log"

  # Prints a debug line either to a file or to stdout
  def printdebug(self, msg):
      # Only run is debug is enabled
      if self.debug:
          # Build the debug string
          newmsg = "\r\nDEBUG--" + str(datetime.datetime.now()) + "# " + msg
          if self.debugtofile:
            try:
                configfile=open(self.debugfilename, "a")
                configfile.write (newmsg)
                configfile.close()
            except:
                print "Error logging to file %s" % self.debugfilename
          else:
                print newmsg
          return None

  # Get the line in the switch config matrix corresponding to the switch specified
  #   'myswitch' parameter could be a switch name, 'leaf' (would return all leaves)
  #   or 'spine' (would return all spines)
  def getSwitch(self, switches, myswitch):
      switchlist = []
      for switch in switches:
        self.printdebug ("Comparing switch name '" + switch[0] + "' with '" + myswitch + "'")
        if myswitch=='leaf' or myswitch=='spine':
            # We compare the type
            if switch[4]==myswitch:
                switchlist.append(switch)
        else:
            if switch[0] == myswitch:
                # We compare the name
                switchlist.append(switch)
      return switchlist

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches) and returns the results in a bidimensional matrix
  #  where the first column contains the switch name, and the second the
  #  JSON output
  def mclid(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      self.printdebug ("Running command " + command + " on " + myswitchname)
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        thisoutput = NXAPITransport.clid (command)
        output.append ( [myswitchname, thisoutput] )
      except:
        self.printdebug ("Error sending command '" + command + "' on " + myswitchname)
        pass
    return output

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches) and returns the results in a bidimensional matrix
  #  where the first column contains the switch name, and the second the
  #  raw output
  def mcli(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      self.printdebug ("Running command " + command + " on " + myswitchname)
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        thisoutput = NXAPITransport.cli (command)
        output.append ( [myswitchname, thisoutput] )
      except:
        self.printdebug ("Error sending command " + command + " on " + myswitchname)
        return False
    return output

  # Runs a command on multiple switches (defined in the class variable
  #  multicli.switches). No values are returned
  def mclic(self, switches, command):
    output=[]
    for switch in switches:
      target_url = "http://"+switch[1]+"/ins"
      myswitchname = switch[0]
      self.printdebug ("Running command " + command + " on " + myswitchname)
      myusername = switch[2]
      mypassword = switch[3]
      NXAPITransport.init(target_url=target_url, username=myusername, password=mypassword)
      try:
        NXAPITransport.clic (command)
      except:
        self.printdebug ("Error sending command " + command + " on " + myswitchname)
        pass

  # Runs a command on a single switch, taking the parameters out of the
  #  class variable 'switches'. Output as JSON
  def sclid (self, myswitchname, command):
    for switch in self.switches:
      if switch[0] == myswitchname:
        target_url = "http://"+switch[1]+"/ins"
        username = switch[2]
        password = switch[3]
        NXAPITransport.init(target_url=target_url, username=username, password=password)
        try:
          output = NXAPITransport.clid (command)
        except:
          self.printdebug ("Error sending command " + command + " on " + myswitchname)
          return False
        return output
    if not output:
      print "Switch %s not found!" % switchName
      return False

  # Runs a command on a single switch, taking the parameters out of the
  #  class variable 'switches'. Output as a raw string
  def scli (self, myswitchname, command):
    for switch in self.switches:
      if switch[0] == myswitchname:
        target_url = "http://"+switch[1]+"/ins"
        username = switch[2]
        password = switch[3]
        NXAPITransport.init(target_url=target_url, username=username, password=password)
        try:
          output = NXAPITransport.cli (command)
        except:
          self.printdebug ("Error sending command " + command + " on " + myswitchname)
          return False
        return output
    if not output:
      print "Switch %s not found!" % myswitchname
      return False


##################
# NXAPI funtions
##################

# Creates a tenant with defined attributes on a switch or set of switches
def createTenant (tenant, l3Vlan, l3Vni, bgpId, whichswitch):
   mymulticli = multicli()
   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)

   # Create VLAN for symmetric routing
   mymulticli.printdebug ("Creating VLAN " + str(l3Vlan))
   command="conf t ; vlan " + str(l3Vlan) + " ; name L3_VNI_" + tenant + " ; vn-segment " + str(l3Vni)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error creating VLAN " + str(l3Vlan))

   # Create VRF
   mymulticli.printdebug ("Creating VRF " + tenant)
   command="conf t ; vrf context " + tenant + " ; vni " + str(l3Vni) + " ; rd auto ; address-family ipv4 unicast ; route-target import "+str(l3Vni)+":"+str(l3Vni)+" ; route-target import "+str(l3Vni)+":"+str(l3Vni)+" evpn ; route-target export "+str(l3Vni)+":"+str(l3Vni)+" ; route-target export "+str(l3Vni)+":"+str(l3Vni)+" evpn"
   try:
      mymulticli.mclic(myswitches, command)
   except Exception as inst:
      print "Error creating VRF " + tenant + ": ", inst

   # Create SVI for symmetric routing
   mymulticli.printdebug ("Creating SVI Vlan" + str(l3Vlan))
   command="conf t ; interface vlan " + str(l3Vlan) + " ; vrf member " + tenant + " ; ip forward ; no shutdown"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error creating SVI Vlan" + str(l3Vlan))
   # Associate VNI to NVE interface
   mymulticli.printdebug ("Associating VNI to interface vne1")
   command="conf t ; interface nve1 ; member vni " + str(l3Vni) + " associate-vrf"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error associating VNI to interface nve1")
   # Add VRF to BGP
   mymulticli.printdebug ("Inserting VRF into BGP")
   command="conf t ; router bgp "+str(bgpId)+" ; vrf " + tenant + " ; address-family ipv4 unicast ; advertise l2vpn evpn"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print "Error inserting VRF into BGP %s" % str(bgpId)

# Delete a tenant from a switch or set of switches
def deleteTenant (tenant, l3Vlan, l3Vni, bgpId, whichswitch):
   mymulticli = multicli()
   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)

   # Add VRF to BGP
   mymulticli.printdebug ("Removing VRF from BGP")
   command="conf t ; router bgp "+str(bgpId)+" ; no vrf " + tenant
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print "Error removing VRF '%s' from BGP %s" % (tenant, str(bgpId))

   # Remove VNI from NVE interface
   mymulticli.printdebug ("Deassociating VNI from interface vne1")
   command="conf t ; interface nve1 ; no member vni " + str(l3Vni) + " associate-vrf"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error deassociating VNI from interface nve1")

   # Remove SVI for symmetric routing
   mymulticli.printdebug ("Removing SVI Vlan" + str(l3Vlan))
   command="conf t ; no interface vlan " + str(l3Vlan)
   try:
       mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing SVI Vlan" + str(l3Vlan))

   # Remove VLAN for symmetric routing
   mymulticli.printdebug ("Removing VLAN " + str(l3Vlan))
   command="conf t ; no vlan " + str(l3Vlan)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing VLAN " + str(l3Vlan))

   # Remove VRF
   mymulticli.printdebug ("Removing VRF " + tenant)
   command="conf t ; no vrf context " + tenant
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing VRF " + tenant)

# Create a VLAN definition on a switch or set of switches
def createVlan (vlanId, vlanName, vni, ipAddress, mcastAddress, tenantName, whichswitch):
   mymulticli = multicli ()
   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)

   #Create VLAN
   mymulticli.printdebug ("Creating VLAN " + str(vlanId))
   command="conf t ; vlan " + str(vlanId) + " ; name " + vlanName + " ; vn-segment " + str(vni)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error creating VLAN " + str(vlanId))

   # Create SVI
   mymulticli.printdebug ("Creating SVI Vlan" + str(vlanId))
   command="conf t ; interface vlan " + str(vlanId) + " ; vrf member " + tenantName + " ; ip address " + ipAddress + " ; fabric forwarding mode anycast-gateway ; no shutdown"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error creating SVI Vlan" + str(vlanId)+" with IP address "+ipAddress+" on VRF "+tenantName)

   # Add to interface NVE1
   mymulticli.printdebug ("Adding VNI to VNE1")
   command="conf t ; interface nve1 ; member vni " + str(vni) + " ; suppress-arp ; mcast-group " + mcastAddress
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error adding VNI to NVE1")

   # Add to EVPN
   mymulticli.printdebug ("Adding VNI to EVPN")
   command="conf t ; evpn ; vni " + str(vni) + " l2 ; rd auto ; route-target import auto ; route-target export auto"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error adding VNI to EVPN")

# Create SVI on a switch or set of switches
def createSVI (vlanId, tenant, ipAddress, whichswitch):
   mymulticli = multicli ()
   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)
   # Build command string
   command="conf t ; interface vlan " + str(vlanId) + " ; vrf member " + tenant + " ; ip address " + ipAddress + " ; fabric forwarding mode anycast-gateway ; no shutdown"
   # Run command
   mymulticli.printdebug ("Creating SVI Vlan " + str(vlanId))
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error creating SVI Vlan" + str(vlanId))

# Delete a VLAN on a switch or set of switches
def deleteVlan (vlanId, vni, whichswitch):
   mymulticli = multicli ()

   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)

   # Remove from EVPN
   mymulticli.printdebug ("Removing VNI from EVPN")
   command="conf t ; evpn ; no vni " + str(vni) + " l2"
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing VNI from EVPN")

   # Remove from interface NVE1
   mymulticli.printdebug ("Removing VNI from VNE1")
   command="conf t ; interface nve1 ; no member vni " + str(vni)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing VNI from NVE1")

   # Remove SVI
   mymulticli.printdebug ("Removing SVI Vlan " + str(vlanId))
   command="conf t ; no interface vlan " + str(vlanId)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing SVI Vlan" + str(vlanId))

   # Remove L2 VLAN
   mymulticli.printdebug ("Removing VLAN " + str(vlanId))
   command="conf t ; no vlan " + str(vlanId)
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error removing VLAN " + str(vlanId))

# Delete an SVI on a switch or a set of switches
def deleteSVI (vlanId, whichswitch):
   mymulticli=multicli()
   # Define the list of switches where the command will be run
   #   It could be all leafs, all switches or one specific switch
   if whichswitch == "all_leafs":
     myswitches = mymulticli.getSwitch (multicli.switches, 'leaf')
   elif whichswitch == "all_switches":
     myswitches = multicli.switches
   else:
     myswitches = mymulticli.getSwitch(multicli.switches, whichswitch)
   # Define command string
   command="config t ;no interface vlan " + str(vlanId)
   mymulticli.printdebug ("Deleting SVI Vlan" + str(vlanId))
   try:
      mymulticli.mclic(myswitches, command)
   except:
      print ("Error deleting SVI Vlan" + str(vlanId) + ". SVI did not exist?")

# Get the new VLANs defined on all switches
def getVlan ():
    command="show vlan"
    try:
      mymulticli = multicli()
      outputs=mymulticli.mclid(multicli.switches, command)
    except Exception as inst:
      print ("Error getting VLAN information: ", inst)
      return False
    if not outputs:
      print "No VLAN information could be retrieved"
      return False
    print "SWITCH       VLAN ID     VLAN Name             VNI    Tenant         IP Address          Multicast group"
    print "======       =======     =========             ===    ======         ==========          ==============="
    for output in outputs:
      mymulticli.printdebug ("Processing JSON: " + str(output[1]))
      try:
        vlans=json.loads(output[1])
        vlans=vlans['TABLE_vlanbrief']['ROW_vlanbrief']
      except:
        print "Error processing JSON output '%s'" % output[1]
        return None
      if not isinstance(vlans, list):
          vlans=[vlans]
      for vlan in vlans:
        try:
           mymulticli.printdebug ("Processing JSON for VLAN: " + str(vlan))
           switchName=output[0]
           vlanId=vlan['vlanshowbr-vlanid-utf']
           vlanName=vlan['vlanshowbr-vlanname']
           vni =getVNI (switchName, vlanId)
           tenantName=getTenant (switchName, vlanId)
           ipAddress=getSviIp (switchName, vlanId)
           mcast=getMcast(switchName, vni)
        except:
            mymulticli.printdebug ("Error processing JSON: " + vlan)
        try:
            print ('{:<13}{:7d}     {:<21} {:<7}{:<15}{:<20}{:<20}'.format(switchName, int(vlanId), vlanName, vni, tenantName, ipAddress, mcast))
        except:
            mymulticli.printdebug ("Error printing info for VLAN " + vlanId + ": " + vlanName + ", " + vni + ", " + tenantName + ", " + ipAddress + ", " + mcast)


# Returns the VNI corresponding to a specific VLAN, on a specific switch
def getVNI (switchName, vlanId):
      command="show vlan id " + str(vlanId) + " vn-segment"
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         vni=segment['TABLE_seginfoid']['ROW_seginfoid']['vlanshowinfo-segment-id']
      except:
         vni=None
      return vni

# Returns the multicast address corresponding to a specific VNI, on a specific switch
def getMcast (switchName, vni):
      command="show nve vni " + str(vni)
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         mcast=segment['TABLE_nve_vni']['ROW_nve_vni']['mcast']
      except:
         mcast=None
      return mcast


# Returns the tenant under which a VLAN is configured in a specific switch
def getTenant (switchName, vlanId):
      command="show vrf interface vlan " + str(vlanId)
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         tenantName=segment['TABLE_if']['ROW_if']['vrf_name']
      except:
         tenantName=None
      return tenantName


# Returns the IP corresponding to a specific SVI on a specific switch
def getSviIp (switchName, vlanId):
      command="show ip interface vlan " + str(vlanId)
      mymulticli = multicli()
      output=mymulticli.sclid(switchName, command)
      try:
         segment=json.loads(output)
         ipAddress=segment['TABLE_intf']['ROW_intf']['prefix']
         ipAddress=ipAddress+"/"+segment['TABLE_intf']['ROW_intf']['masklen']
      except:
         ipAddress=None
      return ipAddress

# Returns a list of tenants configured across all switches
def getTenants ():
    command="show runn | i 'member vni'"
    try:
      mymulticli = multicli()
      outputs=mymulticli.mcli(multicli.switches, command)
    except:
      print "Error getting Tenant information"
      return None
    if not outputs:
      print "No Tenant information could be retrieved"
      return False
    print "Switch       Tenant      L3 VLAN ID       L3 VNI"
    print "======       ======      ==========       ======"
    for output in outputs:
      switchName=output[0]
      lines=output[1].split('\n')
      for line in lines:
        words=line.split()
        # Find out the VNI
        try:
          vni=words[2]
        except:
          mymulticli.printdebug ("No VNI found in string " + line)
        # Make sure there is an "associate-vrf" keyword behind
        try:
            word3 = words[3]
        except:
            pass
        else:
            if word3 == 'associate-vrf':
                vlanId=getVlanFromVni (switchName, vni)
                tenantName=getTenant (switchName, vlanId)
                print ("{:<13}{:<12}{:<17}{}".format(switchName, tenantName, vlanId, vni))

# Returns a VLAN ID configured for a specific VNI on a specific switch
def getVlanFromVni (switchName, vni):
    command="show vxlan"
    try:
      mymulticli = multicli()
      output=mymulticli.scli(switchName, command)
    except Exception as inst:
      print "Error getting VXLAN information", inst
      return None
    if not output:
      print "No VXLAN information could be retrieved"
      return False
    mymulticli.printdebug ("VXLAN output = '\r\n" + output + "'")
    lines=output.split('\n')
    for line in lines:
      words=line.split()
      try:
        thisVlanId=words[0]
        thisVni=words[1]
        mymulticli.printdebug ("VlanID = '" + thisVlanId + "', VNI = '" + thisVni + "'")
        if thisVni == vni:
          return thisVlanId
      except:
        mymulticli.printdebug ("No VNI found in string '" + line + "'")
        pass


############################
# Shell
############################

class evpnCli(cmd2.Cmd):
   '''Welcome to Simple VXLAN EVPN CLI v0.2'''
   prompt='evpn# '
   intro='Simple VXLAN EVPN CLI'

   # Turn debug on / off
   def do_debug (self, line):
        '''Enable debug logging either on screen (default) or to a file
        Syntax:     debug  on|off
        Example:    debug on'''
        debugstate = line
        if debugstate == 'on':
            multicli.debug = True
        elif debugstate == 'off':
            multicli.debug = False
        else:
            print 'Please use debug on|off'

   # Turn debug_to_file on / off
   def do_debugtofile (self, line):
        '''Enable debug logging to a file
        Syntax:     debugtofile  on|off
        Example:    debugtofile on'''
        debugstate = line
        if debugstate == 'on':
            multicli.debugtofile = True

        elif debugstate == 'off':
            multicli.debugtofile = False
        else:
            print 'Please use debug on|off'

   # Define debug file
   def do_debugfilename (self, line):
        '''Specifies filename to write debug info to (remember to enable debugging and file debugging
        Syntax:     debugfilename  <debug_filename>
        Example:    debugfilename evnshell.log'''
        multicli.debugfilename = line

   # Show debug control variables
   def do_show_debug (self, line):
       '''Show the state of debug control variables
       Example: show_debug'''
       if multicli.debug:
           print "Debug:  enabled"
       else:
           print "Debug:  disabled"
       if multicli.debugtofile:
           print "Target: to file"
       else:
           print "Target: to console"
       print     "File:   %s" % multicli.debugfilename

   # Save switch config to a file
   def do_save_switches (self, filename):
     '''Save the switch definitions to a file in JSON format
     Example: save_switches my_lab.conf'''
     jsonstring = json.dumps(multicli.switches)
     try:
       configfile=open(filename, "w")
       configfile.write (jsonstring)
       configfile.close()
     except:
       print "Error writing to %s" % filename

   # Add a new switch
   def do_add_switch (self, line):
      '''Add a switch to the list of managed devices
      Syntax: add_switch leaf|spine <switch_name> <switch_ip> <username> <password>
      Example:
              add_switch leaf n9k-1 10.1.51.155 admin cisco123'''
      args=line.split()
      if len(args)<5:
        print "Not enough arguments provided, please type 'help add_switch' for information on this command"
        return False 
      try:
        switchType = args[0]
        switchName = args[1]
        switchIp   = args[2]
        userName   = args[3]
        password   = args[4]
      except:
        print "Invalid parameters. Type 'help add_switch' for help"
        return False
      if switchType == 'leaf' or switchType == 'spine':
        multicli.switches.append ( [switchName, switchIp, userName, password, switchType] )
      else:
        print "Invalid switch type %s, please select either 'leaf' or 'spine'" % switchType
        return False

   # Display the switches configred
   def do_show_switches (self, line):
     '''Show the switches configured in the system
     Example:  show_switches'''
     print "Type       Name         IP address        Username       Password"
     print "====       ====         ==========        ========       ========"
     for switch in multicli.switches:
       print ('{:<11}{:<13}{:<18}{:<15}{:<15}'.format(switch[4], switch[0], switch[1], switch[2], switch[3]))

   # Save switch config to a file
   def do_save_switches (self, filename):
     '''Save the switch definitions to a file in JSON format
     Example: save_switches my_lab.conf'''
     jsonstring = json.dumps(multicli.switches)
     try:
       configfile=open(filename, "w")
       configfile.write (jsonstring)
       configfile.close()
     except:
       print "Error writing to %s" % filename

   # Load switch config from a file
   def do_load_switches (self, filename):
      '''Load the switch definitions from a file in JSON format (previously saved with save_switches)
      Example: load_switches my_lab.conf'''
      try:
        with open(filename) as json_file:
          multicli.switches = json.load(json_file)
        # Update prompt with filename (without exception)
        fileshort=filename.split(".")[0]
        self.prompt = fileshort+"# "
      except:
       print "Error loading data from %s" % filename
  
   # Add a new VLAN (with SVI, NVI, etc) 
   def do_add_vlan (self, line):
     '''Create one VLAN, including SVI, nve interface definition and evpn definition
     Syntax:  add_vlan <vlan_id> <vlan_name> <vni> <anycast_gw_address> <tenant> <mcast_address> all_leafs|<switch_name>
     Example:
            add_vlan 300 VLAN0300 30300 192.168.30.1/24 Tenant3 224.1.1.30 all_leafs'''
     args=line.split()
     if len(args)<7:
        print "Not enough arguments provided, please type 'help add_vlan' for information on this command"
        return False
     try:
        vlanId      = int(args[0])
        vlanName    = args[1]
        vni         = int(args[2])
        sviIp       = args[3]
        tenant      = args[4]
        mcast       = args[5]
        whichswitch = args[6]
     except:
        print "Invalid parameters. Type 'help add_vlan' for help"
        return False
     createVlan (vlanId, vlanName, vni, sviIp, mcast, tenant, whichswitch)

   # Create a new tenant
   def do_add_tenant (self, line):
     '''Create one tenant, including L3 VLAN/SVI, nve interface definition and evpn definition
     Syntax:  add_tenant <tenant_name> <l3_vlan_id> <l3_vni> <bgp_id> all_leafs|all_switches|<switch_name>
     Example:
            add_tenant tenant1 3900 39000 100 all_leafs'''
     args=line.split()
     if len(args)<5:
        print "Not enough arguments provided, please type 'help add_tenant' for information on this command"
        return False
     try:
        tenantName  = args[0]
        l3VlanId    = int(args[1])
        l3Vni       = int(args[2])
        bgpId       = int(args[3])
        whichswitch = args[4]
     except:
        print "Invalid parameters. Type 'help add_tenant' for help"
        return False
     createTenant (tenantName, l3VlanId, l3Vni, bgpId, whichswitch)

   def do_delete_tenant(self, line):
     '''Delete one tenant, including L3 VLAN/SVI, nve interface definition and evpn definition
     Syntax:  delete_tenant <tenant_name> <l3_vlan_id> <l3_vni> <bgp_id> all_leafs|all_switches|<switch_name>
     Example:
            delete_tenant tenant1 3900 39000 100 all_leafs'''
     args=line.split()
     if len(args)<5:
        print "Not enough arguments provided, please type 'help delete_tenant' for information on this command"
        return False
     try:
        tenantName  = args[0]
        l3VlanId    = int(args[1])
        l3Vni       = int(args[2])
        bgpId       = int(args[3])
        whichswitch = args[4]
     except:
        print "Invalid parameters. Type 'help delete_tenant' for help"
        return False
     deleteTenant (tenantName, l3VlanId, l3Vni, bgpId, whichswitch)

   def do_delete_vlan(self, line):
     '''Remove one VLAN, including SVI, nve interface definition and evpn definition
     Syntax:  delete_vlan <vlan_id> <vni> all_leafs|all_switches|<switch_name>
     Example:
            delete_vlan 300 30300 all_leafs'''
     args=line.split()
     if len(args)<3:
        print "Not enough arguments provided, please type 'help add_vlan' for information on this command"
        return False
     try:
        vlanId      = int(args[0])
        vni         = int(args[1])
        whichswitch = args[2]
     except:
        print "Invalid parameters. Type 'help add_vlan' for help"
        return False
     deleteVlan (vlanId, vni, whichswitch)

   def do_get_vlans (self, arg):
     '''Get a VLAN list
     Example: get_vlans'''
     getVlan ()

   def do_get_tenants (self, arg):
     '''Get a Tenant list
     Example: get_tenants'''
     getTenants ()

   def do_quit (self, arg):
     '''Exit VXLAN EVPN CLI'''
     print ('Bye!')
     return True
   def do_exit (self, arg):
     '''Exit VXLAN EVPN CLI'''
     print ('Bye!')
     return True

   def default (self, arg):
     print ('Whaaat???')

   def emptyline(self):
     return None

if __name__ == '__main__':
   evpnCli().cmdloop()
