#Copyright (C) 2014 Matt Oswalt (http://keepingitclassless.net/)

'''
RoutingTable.py

This is an example of a script that could be written to gather
information from NX-API. Here, we pull the contents of the routing
table and place them into custom objects to be used elsewhere.
'''

from nxapi_utils import NXAPI, xmltodict

#TODO: There may be additional options for other route types

class Prefix(object):
    '''A class to define a route prefix'''
    def __init__(self):
        self.ipprefix = ''
        self.ucast_nhops = ''
        self.mcast_nhops = ''
        self.attached = False
        self.nexthops = []


class NextHop(object):
    '''
    A class to define a next-hop route. Meant to
    be used in an array within the Prefix class
    '''
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

    for key, val in next_hop.iteritems():

        # use setattr to set all of the object attributes
        setattr(nexthop_obj, key, val)

    return nexthop_obj


def process_prefix(prefix_row):
    '''Processes prefix data structure'''

    prefix_obj = Prefix()

    for key, val in prefix_row.iteritems():

        # Check for TABLE_path (nested next_hop structure)
        if key == 'TABLE_path':
            # Next hop is embedded in ['TABLE_path']['ROW_path']
            nexthop_obj = process_nexthop(val['ROW_path'])
            if not nexthop_obj == None:
                prefix_obj.nexthops.append(nexthop_obj)

        else:

            # Swap hyphen for underscore in field names
            key = key.replace('-', '_')

            # use setattr to set all of the object attributes
            setattr(prefix_obj, key, val)

    return prefix_obj


def get_routes(url='', username='', password=''):
    '''
        Retrieves a collection of route entries from the FIB
        of an NXAPI-enabled switch
    '''

    thisnxapi = NXAPI()
    thisnxapi.set_target_url(url)
    thisnxapi.set_username(username)
    thisnxapi.set_password(password)
    thisnxapi.set_msg_type('cli_show')
    thisnxapi.set_cmd('show ip route')
    returndata = thisnxapi.send_req()
    #print returnData[1]  #Uncomment to print the entire XML return

    doc = xmltodict.parse(returndata[1])

    #TODO: need to make more dynamic, for VRFs and IPv6 address families
    prefixtable = doc['ins_api']['outputs']['output']['body']['TABLE_vrf'] \
        ['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']


    for key in prefixtable:
        docsub = prefixtable[key]

    routes = []

    for prefix_row in docsub:           #executes once for every prefix

        this_prefix = process_prefix(prefix_row)

        routes.append(this_prefix)


    # Print out routes
    for route in routes:
        print "The route to ", route.ipprefix, " has ", \
            len(route.nexthops), " next-hop solutions"

        for nexthop in route.nexthops:
            print "via ", nexthop.ipnexthop, "out of", nexthop.ifname

if __name__ == '__main__':
    get_routes('http://10.2.1.8/ins', 'admin', 'Cisco.com')



