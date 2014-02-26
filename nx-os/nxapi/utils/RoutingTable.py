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


class NextHop:
    '''A class to define a next-hop route. Meant to be used in an array within the Prefix class'''
    def __init__(self):
        self.ipnexthop = ''
        self.ifname = ''
        self.uptime = ''
        self.pref = 0
        self.metric = 0
        self.clientname = ''
        self.hoptype = ''
        self.ubest = True



def process_nexthop(next_hop):
    '''Processes nexthop data structure'''

    if not 'ipnexthop' in next_hop:
        # Ignore prefixes with no next hop - not attached?
        return None

    nexthop_obj = NextHop()

    for t_key,t_val in next_hop.iteritems():

        # use setattr to set all of the object attributes
        setattr(nexthop_obj, t_key, t_val)


    return nexthop_obj



def process_prefix(prefix_row):
    '''Takes a prefix from ACI XML call and parses it'''

    prefix_obj = Prefix()

    for k,v in prefix_row.iteritems():

        # Check for TABLE_path (nested next_hop structure)
        if k == 'TABLE_path':
            # Next hop is embedded in ['TABLE_path']['ROW_path']
            nexthop_obj = process_nexthop(v['ROW_path'])
            if not nexthop_obj == None:
                prefix_obj.nexthops.append(nexthop_obj)

        else:

            # Swap hyphen for underscore in field names
            k = k.replace('-', '_')

            # use setattr to set all of the object attributes
            setattr(prefix_obj, k, v)


    return prefix_obj

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

    DEBUG = False
    routes = []

    for prefix_row in docsub:           #executes once for every prefix

        if DEBUG: print prefix_row
        this_prefix = process_prefix(prefix_row)

        routes.append(this_prefix)


    # Print out routes
    for route in routes:
        print "The route to ", route.ipprefix, " has ", len(route.nexthops), " next-hop solutions"
        for nexthop in route.nexthops:
            print "via ", nexthop.ipnexthop, "out of", nexthop.ifname


#And now, the Piece de resistance!!
#Just an example of course, you could do much more with this.
if __name__ == '__main__':
    retrievedRoutes = getRoutes('http://10.2.1.8/ins', 'admin', 'Cisco.com')