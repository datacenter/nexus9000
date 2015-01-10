"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:OS Software Patch Management
:Title:Patch Management
:Short Description:This script is to perform patch related operations
:Long Description:This script is to perform operations like 
    copy, activate, deactivate, remove patch files.
:Input: N9K Address, username, password, tftp_address, smu_file, action
:Output:status/result of the patch management action
"""

import argparse
import getpass
import sys

sys.path.append("../../nx-os/nxapi/utils")

from nxapi_utils import NXAPI
import xmltodict


class Args(object):
    def __init__(self, args): 
        self.n9k = args.hostname
        self.username = args.username
        self.password = args.password
        if not self.password:
            self.password = getpass.getpass()
        self.tftp_address = args.tftp_address
        self.smu_filename = args.smu_filename
        self.action = args.action


def initialize_nxapi_handler(params): 
    nxapi = NXAPI()
    nxapi.set_target_url('http://' + params.n9k  + '/ins')
    nxapi.set_username(params.username)
    nxapi.set_password(params.password)
    nxapi.set_msg_type('cli_conf')
    return nxapi


def check_status(dict_res):
    if dict_res['ins_api']['outputs']['output']['code'] == '200' and \
        dict_res['ins_api']['outputs']['output']['msg'] == 'Success':
        print dict_res['ins_api']['outputs']['output']['body']
        return True
    else:
        print 'Error Msg:' + dict_res['ins_api']['outputs']['output']['msg']
        print 'Code:' + dict_res['ins_api']['outputs']['output']['code']
        return False


def copy_patch_file(params, nxapi_handler):
    print 'copy tftp://'+ params.tftp_address + '/' + params.smu_filename +\
        ' bootflash:// vrf management'
    nxapi_handler.set_cmd('copy tftp://'+ params.tftp_address + '/' +
        params.smu_filename + ' bootflash:// vrf management')
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)
    

def list_patch_file(params, nxapi_handler):
    print 'dir  bootflash:' + params.smu_filename
    nxapi_handler.set_cmd('dir  bootflash:' + params.smu_filename)
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def add_module(params, nxapi_handler):
    print 'install add bootflash:' + params.smu_filename
    nxapi_handler.set_cmd('install add bootflash:' + params.smu_filename)
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def list_inactive_modules(nxapi_handler):
    print 'show install inactive'
    nxapi_handler.set_cmd('show install inactive')
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def activate_patch_file(params, nxapi_handler):
    print 'install activate ' + params.smu_filename
    nxapi_handler.set_cmd('install activate ' + params.smu_filename)
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)

 
def list_active_modules(nxapi_handler):
    nxapi_handler.set_cmd('show install active')
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def deactivate_patch_file(params, nxapi_handler):
    print 'install deactivate ' + params.smu_filename
    nxapi_handler.set_cmd('install deactivate ' + params.smu_filename)
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)

 
def remove_modules(params, nxapi_handler):
    nxapi_handler.set_cmd('install remove ' + params.smu_filename + ' forced')
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def show_install_log(nxapi_handler):
    nxapi_handler.set_cmd('show install log detail')
    returnData = nxapi_handler.send_req()
    dict_res = xmltodict.parse(returnData[1])
    return check_status(dict_res)


def initialize_args():

        parser = argparse.ArgumentParser(
              description='Nexus 9000 OS software patch management utility.',
              epilog="""to openstack cluster.""")

        parser.add_argument('--n9k', '-a', dest='hostname',
            help='Nexus 9XXX hostname or ip address', required=True)
        parser.add_argument('--user', '-u', dest='username',
            help='Username to login to Nexus 9XXX switch', required=True)
        parser.add_argument('--password', '-p', dest='password',
            help='Password to login to Nexus 9XXX switch')
        parser.add_argument('--tftp_address', '-a', dest='tftp_address',
            help='Tftp server ip-address.')
        parser.add_argument('--smu_filename', '-f', dest='smu_filename',
            help='SMU filename.', required=True)
        parser.add_argument('--action', '-o', dest='action', 
            help='Action Install/Remove patch file.', required=True, 
            choices = ['copy', 'activate', 'deactivate', 'remove'])
        args = parser.parse_args()
        return Args(args)


if __name__ == '__main__':

    params = initialize_args()

    nxapi_handler = initialize_nxapi_handler(params)

    if params.action == 'copy':
        if not params.tftp_address:
            params.tftp_address = raw_input('tftp server address:')
        if not copy_patch_file(params, nxapi_handler):
            print 'Failed to copy patch file'
            if not list_patch_file(params, nxapi_handler):
                print 'Failed to copy patch file'
            else:
                print 'Patch file:' + params.smu_filename + ' already present' 
            exit(-1)
        if not list_patch_file(params, nxapi_handler):
            print 'Failed to copy patch file'
            exit(-1)
    elif params.action == 'activate':
        if not add_module(params, nxapi_handler):
            print 'Failed to activate module.'
            exit(-1)
        if not list_inactive_modules(nxapi_handler):
            print 'Failed to list inactive modules.'
            exit(-1)
        if not activate_patch_file(params, nxapi_handler):
            print 'Failed to activate patch file.'
            exit(-1)
        if not list_active_modules(nxapi_handler):
            print 'Failed to list active modules'
            exit(-1)
    elif params.action == 'deactivate':
        if not list_active_modules(nxapi_handler):
            print 'Failed to list active modules'
            exit(-1)
        if not deactivate_patch_file(params, nxapi_handler):
            print 'Failed to deactivate patch file.'
            exit(-1)
        if not list_inactive_modules(nxapi_handler):
            print 'Failed to list inactive modules.'
            exit(-1) 
    elif params.action == 'remove':
        if not list_inactive_modules(nxapi_handler):
            print 'Failed to list inactive modules.'
            exit(-1) 
        if not remove_modules(params, nxapi_handler):
            print 'Failed to remove module.'
            exit(-1)

    if not show_install_log(nxap_handleri):
        print 'Failed to get install log.'
        exit(-1)
    exit(0)
