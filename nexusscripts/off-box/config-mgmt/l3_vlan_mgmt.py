"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:VLAN Configuration Management
:Short Description:This script is to perform L3 VLAN operations
:Long Description:This script is to perform configuration operations
    of L3 VLAN interfaces
:Input:N9K Address, username, password, L3 VLAN parameters
:Output:status/result of the L3 VLAN configuration parameters
"""

import argparse
import getpass
import sys

sys.path.append("../../../nx-os/nxapi/utils")
from nxapi_utils import *
from xmltodict import *

cmd_negate_option = "no"
cmd_config_terminal = "config terminal ;"
cmd_int_ethernet = "interface ethernet %s ;"
cmd_int_no_shutdown = "no shutdown ;"
cmd_no_switchport = "no switchport ;"
cmd_feature_int_vlan = "feature interface-vlan ;"
cmd_create_svi_int = "interface vlan %s ;"
cmd_ip_addr_mask = "ip address %s %s ;"
cmd_ip_addr_len = "ip address %s/%s ;"
cmd_ipv6_addr_len = "ipv6 address %s/%s ;"
cmd_ipv6_addr_link_local = "ipv6 address use-link-local-only ;"
cmd_encap_dot1q_vlanid = "encapsulation dot1Q %s ;"
cmd_show_interfaces = "show interfaces ;"

cmd_int_port_channel = "interface port-channel %s ;"
cmd_int_vlan_interface = "interface vlan %s ;"
cmd_no_shutdown = "no shutdown ;"
cmd_show_vlan_vlanid = "show interface vlan %s ;"
cmd_create_loopback_int = "interface loopback %s ;"
cmd_show_loopback_int = "show interface loopback %s ;"

cmd_add_vrf_member = "vrf member %s ;"
cmd_show_vrf = "show vrf %s interface %s %s ;"
cmd_show_interface = "show interface %s %s ;"

cmd_copy_running_startup = "copy running-config startup-config ;"



class Args(object):

    def __init__(self, args):
        self.n9k = args.hostname
        self.username = args.username
        self.password = args.password
        if not self.password:
            self.password = getpass.getpass()

        self.vlan_id = args.vlan_id
        self.int_type = args.int_type
        self.slot = args.slot
        self.port = args.port
        self.port_channel_id = args.port_channel_id
        self.dot1q_vlanid = args.dot1q_vlanid
        self.loopback_instance = args.loopback_instance
        self.ip_addr = args.ip_addr
        self.ip_len = args.ip_len
        self.ip_mask = args.ip_mask
        self.ipv6_addr = args.ipv6_addr
        self.ipv6_len = args.ipv6_len
        self.ipv6_link_local = args.ipv6_link_local
        self.vrf_member = args.vrf_member


def check_show_status(dict_res):

    if dict_res['ins_api']['outputs']['output']['code'] == '200' and \
        dict_res['ins_api']['outputs']['output']['msg'] == 'Success':
        print dict_res['ins_api']['outputs']['output']['body']
        return True
    else:
        print 'Error Msg:' + dict_res['ins_api']['outputs']['output']['msg']
        print 'Code:' + dict_res['ins_api']['outputs']['output']['code']
        return False


def check_status(dict_res):
    print dict_res
    for output in dict_res['ins_api']['outputs']['output']:
        if output['code'] == '200' and \
            output['msg'] == 'Success':
            print output['body']
        else:
            print 'Error Msg:' + output['msg']
            print 'Code:' + output['code']
            return False
    return True


def initialize_nxapi_handler(params):

    thisNXAPI = NXAPI()
    thisNXAPI.set_target_url('http://' + params.n9k +'/ins')
    thisNXAPI.set_username(params.username)
    thisNXAPI.set_password(params.password)
    thisNXAPI.set_msg_type('cli_conf')
    return thisNXAPI


def create_l3_interface(params, nxapi_handler):

    cmd_str = cmd_config_terminal
    cmd_str += cmd_feature_int_vlan

    if params.int_type == 'ethernet':
        cmd_str += cmd_int_ethernet % (params.slot + "/" + params.port)
        cmd_str += cmd_no_switchport
        if params.dot1q_vlanid:
            cmd_str += cmd_encap_dot1q_vlanid % (params.dot1q_vlanid)
    elif params.int_type == 'port-channel':
        cmd_str += cmd_int_port_channel % (params.port_channel_id)
        cmd_str += cmd_encap_dot1q_vlanid % (params.dot1q_vlanid)
    elif params.int_type == 'vlan':
        cmd_str += cmd_int_vlan_interface % (params.vlan_id)
        cmd_str += cmd_no_shutdown
    elif params.int_type == 'loopback':
        cmd_str += cmd_create_loopback_int % (params.loopback_instance)

    if params.ip_addr and params.ip_len:
        cmd_str += cmd_ip_addr_len % (params.ip_addr, params.ip_len)
    elif params.ip_addr and params.ip_mask:
        cmd_str += cmd_ip_addr_mask % (params.ip_addr, params.ip_mask)

    if params.ipv6_addr and params.ipv6_len:
        cmd_str += cmd_ipv6_addr_len % (params.ipv6_addr, params.ipv6_len)
    if params.ipv6_link_local:
        cmd_str += cmd_ipv6_addr_link_local

    if params.vrf_member:
        cmd_str += cmd_add_vrf_member % (params.vrf_member)

    cmd_str += cmd_int_no_shutdown
    cmd_str += cmd_copy_running_startup

    print cmd_str
    nxapi_handler.set_cmd(cmd_str)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def show_interface(params, nxapi_handler):
    cmd_str = ''
    if params.int_type == 'ethernet':
        cmd_str += cmd_show_interface %\
            (params.int_type, "%s/%s" %(params.slot, params.port))
    elif params.int_type == 'port-channel':
        cmd_str += cmd_show_interface % params.int_type, params.port_channel_id
    elif params.int_type == 'vlan':
        cmd_str += cmd_show_interface % params.int_type, params.vlan_id
    elif params.int_type == 'loopback':
        cmd_str += cmd_show_interface % params.int_type, params.loopback_instance
    print cmd_str
    nxapi_handler.set_cmd(cmd_str)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_show_status(dict_res)

def initialize_args():

    parser = argparse.ArgumentParser(
                description='Nexus 9000 L3 VLAN interface configuration mgmt.',
                epilog="""   """)

    parser.add_argument('--n9k', '-a', dest='hostname',
        help='Nexus 9XXX hostname or ip address', required=True)
    parser.add_argument('--user', '-u', dest='username',
        help='Username to login to Nexus 9XXX switch', required=True)
    parser.add_argument('--password', '-c', dest='password',
        help='Password to login to Nexus 9XXX switch')
    parser.add_argument('--interface_type', '-t', dest='int_type',
        help='Interface type',
        choices={'ethernet', 'port-channel', 'vlan', 'loopback'})
    parser.add_argument('--slot-id', '-s', dest='slot',
        help="ethernet interface slot-id")
    parser.add_argument('--port-id', '-p', dest='port',
        help="ethernet interface port-id")
    parser.add_argument('--port-channel-id', '-n', dest='port_channel_id',
        help='Encaptulation vlan-id')
    parser.add_argument('--encap_vlanid', '-e', dest='dot1q_vlanid',
        help='Encaptulation vlan-id')
    parser.add_argument('--vlanid', '-v', dest='vlan_id',
        help='VLAN id')
    parser.add_argument('--loopback_instnace_id', '-o', dest='loopback_instance',
        help='Loopback interface instance id')
    parser.add_argument('--ip-address', '-4', dest='ip_addr',
        help='IPv4 address')
    parser.add_argument('--ip-address-length', '-l', dest='ip_len',
        help='IPv4 address length')
    parser.add_argument('--ip-address-mask', '-m', dest='ip_mask',
        help='IPv4 address length')
    parser.add_argument('--ipv6-address', '-6', dest='ipv6_addr',
        help='IPv6 address')
    parser.add_argument('--ipv6-address-length', '-k', dest='ipv6_len',
        help='IPv6 address length')
    parser.add_argument('--ipv6-use-link-local-address', '-q', dest='ipv6_link_local',
        help='IPv6 address length', type=bool, default=False)
    parser.add_argument('--vrf-member-id', '-r', dest='vrf_member',
        help='IPv6 address length')

    args = parser.parse_args()
    return Args(args)


if __name__ == '__main__':

    params = initialize_args()
    nxapi_handler = initialize_nxapi_handler(params)
    create_l3_interface(params, nxapi_handler)
    show_interface(params, nxapi_handler)
    exit(0)
