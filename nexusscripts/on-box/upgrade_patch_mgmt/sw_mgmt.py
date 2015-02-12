"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:OS Software Upgrade Management
:Title: Software Management
:Short Description:This script is to perform Software management operations 
:Long Description:This script is to perform operations like 
    copy, upgrade, downgrade, remove switch images.
:Input: N9K Address, username, password, tftp_address, image_filename, action
:Output:status/result of the software management action
"""

import argparse
from cli import *
import sys

class Args(object):

    def __init__(self, args): 
        self.tftp_address = args.tftp_address
        self.image_filename = args.image_filename
        self.action = args.action


def copy_image_file(params):

    print 'copy tftp://'+ params.tftp_address + '/' + params.image_filename +\
        ' bootflash:// vrf management'
    return_xml = cli('copy tftp://'+ params.tftp_address + '/' +\
        params.image_filename + ' bootflash:// vrf management')
    print return_xml


def verify_active_sessions():
    print 'show configuration session summary'
    return_xml = cli('show configuration session summary')
    print return_xml


def check_image_incompatability(params):
    print 'show incompatability nxos bootflash:' +\
        params.image_filename
    return_xml = cli('show incompatability nxos bootflash:' +\
        params.image_filename)
    print return_xml


def remove_image(params):
    print 'delete bootflash:' + params.image_filename + " no-prompt"
    return_xml = cli('delete bootflash:' +\
        params.image_filename + " no-prompt")
    print return_xml


def check_install_all_impact(params):
    print 'show install all impact nxos bootflash:' +\
        params.image_filename
    return_data = cli('show install all impact nxos bootflash:' +\
        params.image_filename)
    print return_data
    

def copy_run_cfg_start_cfg():
    print 'copy running-config startup-config'
    return_data = cli('copy running-config startup-config')
    print return_data


def install_all_nxos_image(params):
    print 'install all parallel nxos bootflash:' +\
        params.image_filename
    return_data = cli('install all parallel nxos bootflash:' +\
        params.image_filename)
    print return_data


def initialize_args():

    parser = argparse.ArgumentParser(
                description='Nexus 9000 OS software patch management utility.',
                epilog="""   """)

    parser.add_argument('--tftp-address', '-a', dest='tftp_address',
        help='Tftp server ip-address.')
    parser.add_argument('--image_filename', '-f', dest='image_filename',
        help='Image filename.', required=True)
    parser.add_argument('--action', '-o', dest='action',
        help='Action Upgrade/Downgrade switch image.',
        required=True, choices = ['copy', 'upgrade', 'downgrade', 'remove'])
    args = parser.parse_args()
    return Args(args)

if __name__ == '__main__':

    params = initialize_args()

    if params.action == 'copy':
        copy_image_file(params)
    elif params.action == 'upgrade':
        verify_active_sessions()
    elif params.action == 'downgrade':
        check_image_incompatability(params)
    elif params.action == 'remove':
        remove_image(params)

    if params.action in {'upgrade','downgrade'}:
        check_install_all_impact(params)
        copy_run_cfg_start_cfg()
        install_all_nxos_image(params)
    exit(0)
