"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:Config-Mgmt
:Box Type:Off-Box
:Title:VLAN Configuration Management
:Short Description:This script is to perform VLAN operations
:Long Description:This script is to perform configuration operations
    of VLAN interfaces
:Input:N9K Address, username, password, VLAN parameters
:Output:status/result of the VLAN configuration parameters
"""

import argparse
import getpass
import sys

sys.path.append("../../../nx-os/nxapi/utils")
from nxapi_utils import *
from xmltodict import *

cmd_config_terminal = "config terminal ;"
cmd_vlan_id_range = "vlan %s ;"
cmd_no_vlan_id_range = "no vlan %s ;"
cmd_vlan_media = "media enet ;"
cmd_vlan_name = "name %s ;"
cmd_vlan_state = "state %s ;"
cmd_vlan_no_shutdown = "no shutdown ;"
cmd_vlan_long_name = "system vlan long-name ;"

cmd_copy_running_startup = "copy running-config startup-config ;"

cmd_vlan_show = "show running-config vlan %s ;"
cmd_vlan_summary = "show vlan summary ;"
cmd_vtp_status = "show vtp status ;"


class Args(object):

    def __init__(self, args):
        self.n9k = args.hostname
        self.username = args.username
        self.password = args.password
        if not self.password:
            self.password = getpass.getpass()

        self.vlan = args.vlan
        self.vlan_name = args.vlan_name
        self.vlan_state = args.vlan_state
        self.action = args.action
        self.vlan_shutdown = args.vlan_shutdown


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


def configure_vlan(params, nxapi_handler):

    cmd_str = cmd_config_terminal 
    if params.action == 'configure':
        cmd_str += cmd_vlan_id_range % (params.vlan)
        if params.vlan_name:
            cmd_str += cmd_vlan_name % (params.vlan_name)
        if params.vlan_state:
            cmd_str += cmd_vlan_state % (params.vlan_state)
        if not params.vlan_shutdown:
            cmd_str += cmd_vlan_no_shutdown
    elif params.action == 'remove':
        cmd_str += cmd_no_vlan_id_range % (params.vlan)

    cmd_str += cmd_copy_running_startup

    print cmd_str
    nxapi_handler.set_cmd(cmd_str)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def show_vlan(params, nxapi_handler):
    cmd_str = cmd_vlan_show % (params.vlan)

    print cmd_str
    nxapi_handler.set_cmd(cmd_str)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_show_status(dict_res)


def initialize_args():

    parser = argparse.ArgumentParser(
        description='Nexus 9000 VLAN configuration',
        epilog="""   """)

    parser.add_argument('--n9k', '-a', dest='hostname',
    help='Nexus 9XXX hostname or ip address', required=True)
    parser.add_argument('--user', '-u', dest='username',
        help='Username to login to Nexus 9XXX switch', required=True)
    parser.add_argument('--password', '-c', dest='password',
        help='Password to login to Nexus 9XXX switch')
    parser.add_argument('--vlan', '-v', dest='vlan',
        help='VLAN id/range', required=True)
    parser.add_argument('--vlan-name', '-n', dest='vlan_name',
        help='VLAN name')
    parser.add_argument('--state', '-s', dest='vlan_state',
        help='VLAN state', choices={'active', 'suspend'}, default='active')
    parser.add_argument('--shutdown', '-d', dest='vlan_shutdown',
        help='VLAN state', type=bool, default=False)
    parser.add_argument('--action', '-o', dest='action',
        help='VLAN state', choices={'configure', 'remove', 'show'})

    args = parser.parse_args()
    return Args(args)


if __name__ == '__main__':

    params = initialize_args()
    nxapi_handler = initialize_nxapi_handler(params)
    if params.action in {'remove', 'configure'}:
        configure_vlan(params, nxapi_handler)
        show_vlan(params, nxapi_handler)
    else:
        show_vlan(params, nxapi_handler)

    exit(0)
