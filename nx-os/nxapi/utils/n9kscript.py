# "...because the ones who are crazy enough to think that they can change the world, are the ones who do." --RIP Steve Jobs

from nxapi_utils import *
from collections import OrderedDict
from array import *

#Installed lxml from here: http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml 
#I'm stupid and am currently developing on Windows. Finding out that it's more trouble than it's worth. :(

thisNXAPI = NXAPI()
thisNXAPI.set_target_url('http://10.2.1.8/ins')
thisNXAPI.set_username('admin')
thisNXAPI.set_password('Cisco.com')
thisNXAPI.set_msg_type('cli_show')
thisNXAPI.set_cmd('show ip route')
returnData = thisNXAPI.send_req()
#print returnData[1]

doc = xmltodict.parse(returnData[1])

#TODO: As-is, this would entirely bypass (I think) the IPv6 address family. Need to go back and rewrite to be a little less static
for k ,v in doc['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix'].iteritems():
        docsub = v

for prefix_row in docsub:
 for key in prefix_row.keys():  # a simple display of keys and their values
    item_type=type(prefix_row[key])
    if item_type == OrderedDict:
        for t_key in prefix_row[key].keys():
            if type(prefix_row[key][t_key]) == unicode:
                print key,"==>",t_key,"==>",prefix_row[key][t_key]
            else:   #assuming ordered dictionary
                for tr_key in prefix_row[key][t_key].keys():
                    print key,"==>",t_key,"==>",tr_key,"==>",prefix_row[key][t_key][tr_key]
    elif item_type == unicode:
        print key,"==>",prefix_row[key]
    else:
        print "Warning: Unable to parse item type",item_type



class Prefix:
    '''A class to define a route prefix'''
    def __init__(self):
        self.ipprefix = ''
        self.ucast_nhops = ''
        self.mcast_nhops = ''
        self.attached = False #Comes in as a string, need to convert to boolean when instantiating this class
        self.nexthops = []

    def set_ipprefix(self, ipprefix=''):
        self.ipprefix = ipprefix

    def set_ucast_nhops(self, ucast_nhops=''):
        self.ucast_nhops = ucast_nhops

    def set_mcast_nhops(self, mcast_nhops=''):
        self.mcast_nhops = mcast_nhops

    def set_attached(self, attached=False): #Comes in as a string, need to convert to boolean when instantiating this class
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
        self.ubest = True #Comes in as a string, need to convert to boolean when instantiating this class

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

    def set_ubest(self, ubest=True): #Comes in as a string, need to convert to boolean when instantiating this class
        self.ubest = ubest