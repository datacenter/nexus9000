#Copyright (C) 2013 Matt Oswalt (http://keepingitclassless.net/) 

from nxapi_utils import *
from collections import OrderedDict
from array import *

#TODO: need to make more dynamic, for VRFs and IPv6 address families. Also need to figure out the various route types and make sure your classes are dynamic enough.

class Prefix:
    '''A class to define a route prefix'''
    def __init__(self):
        self.ipprefix = ''
        self.ucast_nhops = ''
        self.mcast_nhops = ''
        self.attached = False
        self.nexthops = []

    def set_ipprefix(self, ipprefix=''):
        self.ipprefix = ipprefix

    def set_ucast_nhops(self, ucast_nhops=''):
        self.ucast_nhops = ucast_nhops

    def set_mcast_nhops(self, mcast_nhops=''):
        self.mcast_nhops = mcast_nhops

    def set_attached(self, attached=False):
        self.attached = attached

    def set_nexthops(self, nexthops=[]):
        self.nexthops = nexthops


class NextHop:
    '''A class to define a next-hop route. Meant to be used in an array within the Prefix class'''
    #TODO: Looks like the number of fields that comes in varies when it's an OSPF route vs static or direct. need to test with various route types and ensure this data structure is appropriate for all
    def __init__(self):
        self.ipnexthop = ''
        self.ifname = ''
        self.uptime = ''
        self.pref = 0
        self.metric = 0
        self.clientname = ''
        self.hoptype = ''
        self.ubest = True

    def set_ipnexthop(self, ipnexthop=''):
        self.ipnexthop = ipnexthop

    def set_ifname(self, ifname=''):
        self.ifname = ifname

    def set_uptime(self, uptime=''):
        self.uptime = uptime

    def set_pref(self, pref=0):
        self.pref = pref

    def set_metric(self, metric=0):
        self.metric = metric

    def set_clientname(self, clientname=''):
        self.clientname = clientname

    def set_hoptype(self, hoptype=''):
        self.hoptype = hoptype

    def set_ubest(self, ubest=True):
        self.ubest = ubest

def getRoutes(url='',username='',password=''):
    thisNXAPI = NXAPI()
    thisNXAPI.set_target_url(url)
    thisNXAPI.set_username(username)
    thisNXAPI.set_password(password)
    thisNXAPI.set_msg_type('cli_show')
    thisNXAPI.set_cmd('show ip route')
    returnData = thisNXAPI.send_req()
    #print returnData[1]  #Uncomment to print the entire XML return

    doc = xmltodict.parse(returnData[1])

    #TODO: As-is, this would probably disregard any VRF other than "default" and also probably ignore IPv6. Need to go back and rewrite to be a little less static
    for k ,v in doc['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix'].iteritems():
            docsub = v

    routes = []

    #Commented out but left most of the "print" lines that output dictionary structure. Can uncomment for debugging purpsoes.
    for prefix_row in docsub: #executes once for every prefix
        thisPrefix = Prefix()
        for key in prefix_row.keys():  # a simple display of keys and their values
            item_type=type(prefix_row[key])
            if item_type == OrderedDict:
                #If another OrderedDict, then these are properties of next-hop routes on this prefix and should be iterated through further.
                for t_key in prefix_row[key].keys():
                    if type(prefix_row[key][t_key]) == unicode:
                        print key,"==>",t_key,"==>",prefix_row[key][t_key] #This is here just to be exhaustive. Current output shouldn't give any unicode values here, only another OrderedDict
                    else:   #assuming ordered dictionary
                        #This is a single next-hop. All keys and values below are properties of this next-hop route.
                        thisNextHop = NextHop()
                        for tr_key in prefix_row[key][t_key].keys():
                            if tr_key == 'ipnexthop':
                                thisNextHop.set_ipnexthop(prefix_row[key][t_key][tr_key])
                            if tr_key == 'ifname':
                                thisNextHop.set_ifname(prefix_row[key][t_key][tr_key])
                            if tr_key == 'pref':
                                thisNextHop.set_pref(prefix_row[key][t_key][tr_key])
                            if tr_key == 'metric':
                                thisNextHop.set_metric(prefix_row[key][t_key][tr_key])
                            if tr_key == 'clientname':
                                thisNextHop.set_clientname(prefix_row[key][t_key][tr_key])
                            if tr_key == 'type':
                                thisNextHop.set_hoptype(prefix_row[key][t_key][tr_key])
                            if tr_key == 'ubest':
                                thisNextHop.set_ubest(bool(prefix_row[key][t_key][tr_key]))
                            #print key,"==>",t_key,"==>",tr_key,"==>",prefix_row[key][t_key][tr_key]
                        thisPrefix.nexthops.append(thisNextHop)
            elif item_type == unicode:
                #If unicode, then these are the properties for this entire prefix.
                if key == 'ipprefix':
                    thisPrefix.set_ipprefix(prefix_row[key])
                elif key == 'ucast-nhops':
                    thisPrefix.set_ucast_nhops(prefix_row[key])
                elif key == 'mcast-nhops':
                    thisPrefix.set_mcast_nhops(prefix_row[key])
                elif key == 'attached':
                    thisPrefix.set_attached(bool(prefix_row[key]))
                #print key,"==>",prefix_row[key]
            else:
                print "Warning: Unable to parse item type",item_type
        routes.append(thisPrefix)
    return routes


#And now, the Piece de resistance!!
#Just an example of course, you could do much more with this.

retrievedRoutes = getRoutes('http://10.2.1.8/ins', 'admin', 'Cisco.com')

for route in retrievedRoutes:
    print "The route to ", route.ipprefix, " has ", len(route.nexthops), " next-hop solutions"
    for nexthop in route.nexthops:
        print "via ", nexthop.ipnexthop, "out of", nexthop.ifname