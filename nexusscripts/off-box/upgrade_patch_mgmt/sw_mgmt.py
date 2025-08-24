"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:OS-Mgmt
:Box Type:Off-Box
:Title:Software Management
:Short Description:This script is to perform Software management operations 
:Long Description:This script is to perform operations like 
    copy, upgrade, downgrade, remove switch images.
:Input:N9K Address, username, password, tftp_address, image_filename, action
:Output:status/result of the software management action
"""

import argparse
import getpass
import sys

sys.path.append("../../../nx-os/nxapi/utils")
from nxapi_utils import *
from xmltodict import *


class Args(object):

    def __init__(self, args): 
        self.n9k = args.hostname
        self.username = args.username
        self.password = args.password
        if not self.password:
            self.password = getpass.getpass()
        self.tftp_address = args.tftp_address
        self.timeout = args.timeout
        self.image_filename = args.image_filename
        self.action = args.action


def initialize_nxapi_handler(params):

    thisNXAPI = NXAPI()
    thisNXAPI.set_target_url('http://' + params.n9k +'/ins')
    thisNXAPI.set_username(params.username)
    thisNXAPI.set_password(params.password)
    thisNXAPI.set_timeout(params.timeout)
    thisNXAPI.set_msg_type('cli_conf')
    return thisNXAPI


def check_status(dict_res):

    if dict_res['ins_api']['outputs']['output']['code'] == '200' and \
        dict_res['ins_api']['outputs']['output']['msg'] == 'Success':
        print dict_res['ins_api']['outputs']['output']['body']
        return True
    else:
        print 'Error Msg:' + dict_res['ins_api']['outputs']['output']['msg']
        print 'Code:' + dict_res['ins_api']['outputs']['output']['code']
        return False


def copy_image_file(params, nxapi_handler):

    print 'copy tftp://'+ params.tftp_address + '/' + params.image_filename +\
        ' bootflash:// vrf management'
    nxapi_handler.set_cmd('copy tftp://'+ params.tftp_address + '/' +\
        params.image_filename + ' bootflash:// vrf management')
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def verify_active_sessions(nxapi_handler):
    print 'show configuration session summary'
    nxapi_handler.set_cmd('show configuration session summary')
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def check_image_incompatibility(params, nxapi_handler):
    nxapi_handler.set_cmd('show incompatibility nxos bootflash:' +\
        params.image_filename)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def remove_image(params, nxapi_handler):
    print 'delete bootflash:' + params.image_filename + " no-prompt"
    nxapi_handler.set_cmd('delete bootflash:' +\
        params.image_filename + " no-prompt")
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def check_install_all_impact(params, nxapi_handler):
    print 'show install all impact nxos bootflash:' +\
        params.image_filename
    nxapi_handler.set_cmd('show install all impact nxos bootflash:' +\
        params.image_filename)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)
    

def copy_run_cfg_start_cfg(nxapi_handler):
    print 'copy running-config startup-config'
    nxapi_handler.set_cmd('copy running-config startup-config')
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def install_all_nxos_image(params, nxapi_handler):
    print 'install all parallel nxos bootflash:' +\
        params.image_filename
    nxapi_handler.set_cmd('install all parallel nxos bootflash:' +\
        params.image_filename)
    return_xml = nxapi_handler.send_req()
    dict_res = xmltodict.parse(return_xml[1])
    return check_status(dict_res)


def initialize_args():

    parser = argparse.ArgumentParser(
                description='Nexus 9000 OS software patch management utility.',
                epilog="""   """)

    parser.add_argument('--n9k', '-i', dest='hostname',
        help='Nexus 9XXX hostname or ip address', required=True)
    parser.add_argument('--user', '-u', dest='username',
        help='Username to login to Nexus 9XXX switch', required=True)
    parser.add_argument('--password', '-p', dest='password',
        help='Password to login to Nexus 9XXX switch')
    parser.add_argument('--tftp-address', '-a', dest='tftp_address',
        help='Tftp server ip-address.')
    parser.add_argument('--image_filename', '-f', dest='image_filename',
        help='Image filename.', required=True)
    parser.add_argument('--timeout', '-t', dest='timeout',
        help='Connection Timeout.', type=int, default=600)
    parser.add_argument('--action', '-o', dest='action',
        help='Action Upgrade/Downgrade switch image.',
        required=True, choices = ['copy', 'upgrade', 'downgrade', 'remove'])
    args = parser.parse_args()
    return Args(args)

if __name__ == '__main__':

    params = initialize_args()
    nxapi_handler = initialize_nxapi_handler(params)

    if params.action == 'copy':
        if not copy_image_file(params, nxapi_handler):
            print 'Failed to copy image file'
            exit(-1)
    elif params.action == 'upgrade':
        # pre-requisite check before upgrading
        if not verify_active_sessions(nxapi_handler):
            print 'Failed to verify active sessions'
            exit(-1)
    elif params.action == 'downgrade':
        if not check_image_incompatibility(params, nxapi_handler):
            print 'Failed to check image incompatibility'
            exit(-1)
    elif params.action == 'remove':
        if not remove_image(params, nxapi_handler):
            print 'Failed to remove image'
            exit(-1)

    if params.action in {'upgrade','downgrade'}:
        if not check_install_all_impact(params, nxapi_handler):
            print 'Failed to check install all impact.'
            exit(-1)
        if not copy_run_cfg_start_cfg(nxapi_handler):
            print 'Failed to copy running-config to startup-config.'
            exit(-1)
        if not install_all_nxos_image(params, nxapi_handler):
            print 'Failed to update switch image file.'
            exit(-1)
    exit(0)
