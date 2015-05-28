"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:VLAN Configuration Management
:Short Description:This script is to perform L2 VLAN operations
:Long Description:This script is to perform configuration operations
    of L2 VLAN interfaces
:Input:N9K Address, username, password, L2 VLAN parameters
:Output:status/result of the L2 VLAN configuration parameters
"""

import argparse
import getpass
import sys

sys.path.append("../../../nx-os/nxapi/utils")
from nxapi_utils import *
from xmltodict import *

cmd_config_terminal = "config terminal ;"
cmd_int_ethernet = "interface ethernet %s/%s ;"
cmd_int_port_channel = "interface port-channel %s ;"
cmd_int_no_shutdown = "no shutdown ;"
cmd_switchport_mode = "switchport mode %s ;"
cmd_switchport_access_vlan = "switchport access vlan %s ;"
cmd_switchport = "switchport ;"
cmd_switchport_host = "switchport host ;"
cmd_switchport_trunk_native = "switchport trunk native vlan %s ;"
cmd_switchport_trunk_allowed_vlan = "switchport trunk allowed vlan %s %s ;"
cmd_default_int = "default interface int-if %s ;"
cmd_switchport_autostate_exclude = "switchport autostate exclude ;"
cmd_switchport_autostate_exclude_vlan =\
    "switchport autostate exclude vlan %s ;"
cmd_svi_autostate_disable = "system default interface-vlan no autostate ;"

cmd_vlan_tag_native = "vlan dot1q tag native ;"
cmd_sys_default_port_mode_2_l2 = "system default switchport ;"

cmd_copy_running_startup = "copy running-config startup-config ;"
cmd_show_interface = "show running-config interface %s  %s ;"

class Args(object):

    def __init__(self, args):
        self.n9k = args.hostname
        self.username = args.username
        self.password = args.password
        if not self.password:
            self.password = getpass.getpass()
        self.vlan_list = args.vlan_list
        self.int_type = args.int_type
        self.port_channel_id = args.port_channel_id
        self.slot = args.slot
        self.port = args.port
        self.switchport_mode = args.switchport_mode
        self.trunk_allowed_vlan_oper = args.trunk_allowed_vlan_oper
        self.trunk_native_id = args.trunk_native_id
        self.tag_native_vlan = args.tag_native_vlan


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


def create_l2_interface(params, nxapi_handler):

    cmd_str = cmd_config_terminal
    if params.tag_native_vlan:
        cmd_str += cmd_vlan_tag_native

    if params.int_type == 'ethernet':
        cmd_str += cmd_int_ethernet % (params.slot, params.port)
    if params.int_type == 'port-channel':
        cmd_str += cmd_int_port_channel % (params.port_channel_id)

    cmd_str += cmd_switchport

    if params.switchport_mode == 'access':
        cmd_str += cmd_switchport_mode % (params.switchport_mode)
        cmd_str += cmd_switchport_access_vlan % (params.vlan_list)
    elif params.switchport_mode == 'host':
        cmd_str += cmd_switchport_host
    elif params.switchport_mode == 'trunk':
        cmd_str += cmd_switchport_mode % (params.switchport_mode)
        if params.trunk_native_id:
            cmd_str += cmd_switchport_trunk_native % (params.trunk_native_id)
        if params.trunk_allowed_vlan_oper in {'add', 'remove', 'except'}:
            cmd_str += cmd_switchport_trunk_allowed_vlan %\
                (params.trunk_allowed_vlan_oper, params.vlan_list)
        elif params.trunk_allowed_vlan_oper in {'all', 'none'}:
            cmd_str += cmd_switchport_trunk_allowed_vlan %\
                (params.trunk_allowed_vlan_oper, ' ')
        else:
            cmd_str += cmd_switchport_trunk_allowed_vlan %\
                (params.vlan_list, ' ')

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
        cmd_str += cmd_show_interface % (params.int_type,\
            params.port_channel_id)
    print cmd_str
    nxapi_handler.set_cmd(cmd_str)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_show_status(dict_res)
    


def initialize_args():

    parser = argparse.ArgumentParser(
                description='Nexus 9000 L2 VLAN interface configuration mgmt.',
                epilog="""   """)

    parser.add_argument('--n9k', '-a', dest='hostname',
        help='Nexus 9XXX hostname or ip address', required=True)
    parser.add_argument('--user', '-u', dest='username',
        help='Username to login to Nexus 9XXX switch', required=True)
    parser.add_argument('--password', '-c', dest='password',
        help='Password to login to Nexus 9XXX switch')
    parser.add_argument('--interface_type', '-t', dest='int_type',
        help='Interface type',
        choices={'ethernet', 'port-channel'})
    parser.add_argument('--slot-id', '-s', dest='slot',
        help="ethernet interface slot-id")
    parser.add_argument('--port-id', '-p', dest='port',
        help="ethernet interface port-id")
    parser.add_argument('--port-channel-id', '-n', dest='port_channel_id',
        help='port-channel id')
    parser.add_argument('--switchport-mode', '-m', dest='switchport_mode',
        help='switchport mode \'access|trunk|host\'',
        choices={'access', 'trunk', 'host'})
    parser.add_argument('--trunk-allowed-vlan-oper', '-o',
        dest='trunk_allowed_vlan_oper', help='trunk allowed vlan oper',
        choices={'add', 'remove', 'except', 'all', 'none'}),
    parser.add_argument('--vlan-list', '-v', dest='vlan_list',
        help='VLAN ID/list')
    parser.add_argument('--trunk-native-vlan-id', '-k', dest='trunk_native_id',
        help='Trunk native VLAN ID')
    parser.add_argument('--tag-native-vlan-traffic', '-r',
        dest='tag_native_vlan',
        help='Tag native VLAN traffic', type=bool, default=False)

    args = parser.parse_args()
    return Args(args)


if __name__ == '__main__':

    params = initialize_args()
    nxapi_handler = initialize_nxapi_handler(params)
    create_l2_interface(params, nxapi_handler)
    show_interface(params, nxapi_handler)

    exit(0)
