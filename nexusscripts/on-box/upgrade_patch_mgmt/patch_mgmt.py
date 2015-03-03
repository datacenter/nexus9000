"""Script Cataloging Information
:Product Info:Nexus::9000::9516::NX-OS Release 6.2
:Category:OS Software Patch Management
:Title:Patch Management
:Short Description:This script is to perform patch related operations
:Long Description:This script is to perform operations like 
    copyactivatedeactivateremove patch files.
:Input: tftp_addresssmu_fileaction
:Output:status/result of the patch management action
"""

"""Examples

(1) install activate
(2) install commit (active)
(3) install deactivate
(4) install commit (inactive)
(5) install remove

(1) install activate 
root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action activate
install add bootflash:n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 179 completed successfully at Tue Jan 27 09:13:02 2015
show install inactive
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
install activate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 180 completed successfully at Tue Jan 27 09:13:08 2015
Active Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Tue Jan 27 09:13:08 2015
Install operation 180 by user  admin  at Tue Jan 27 09:13:02 2015
Install activate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 180 completed successfully at Tue Jan 27 09:13:08 2015

root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action status
Inactive Packages:
Active Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Committed Packages:
Tue Jan 27 09:13:39 2015
Install operation 180 by user  admin  at Tue Jan 27 09:13:02 2015
Install activate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 180 completed successfully at Tue Jan 27 09:13:08 2015

(2) install commit (active)
root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --use r admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action commit_active
Active Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 181 completed successfully at Tue Jan 27 09:14:09 2015
Tue Jan 27 09:14:09 2015
Install operation 181 by user  admin  at Tue Jan 27 09:14:07 2015
Install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 181 completed successfully at Tue Jan 27 09:14:09 2015

root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --use r admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action status
Inactive Packages:
Active Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Committed Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Tue Jan 27 09:14:17 2015
Install operation 181 by user  admin  at Tue Jan 27 09:14:07 2015
Install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 181 completed successfully at Tue Jan 27 09:14:09 2015

(3) install deactivate 
root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action deactivate
Active Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
install deactivate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 182 completed successfully at Tue Jan 27 09:15:10 2015
show install inactive
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Tue Jan 27 09:15:10 2015
Install operation 182 by user  admin  at Tue Jan 27 09:15:04 2015
Install deactivate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 182 completed successfully at Tue Jan 27 09:15:10 2015

root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action status
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Active Packages:
Committed Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Tue Jan 27 09:15:18 2015
Install operation 182 by user  admin  at Tue Jan 27 09:15:04 2015
Install deactivate n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 182 completed successfully at Tue Jan 27 09:15:10 2015

(4) install commit (inactive)
root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action commit_inactive
show install inactive
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 184 completed successfully at Tue Jan 27 09:16:03 2015
Tue Jan 27 09:16:03 2015
Install operation 184 by user  admin  at Tue Jan 27 09:16:01 2015
Install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 184 completed successfully at Tue Jan 27 09:16:03 2015

root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action status
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Active Packages:
Committed Packages:
Tue Jan 27 09:16:10 2015
Install operation 184 by user  admin  at Tue Jan 27 09:16:01 2015
Install commit n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 184 completed successfully at Tue Jan 27 09:16:03 2015

(5) install remove
root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action remove
show install inactive
Inactive Packages:
        n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 185 completed successfully at Tue Jan 27 09:16:46 2015
Tue Jan 27 09:16:46 2015
Install operation 185 by user  admin  at Tue Jan 27 09:16:46 2015
Install remove n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 185 completed successfully at Tue Jan 27 09:16:46 2015

root@aio178:/home/localadmin/nexus9000/nexusscripts/off-box/upgrade_patch_mgmt# python patch_mgmt.py --n9k 10.1.150.11 --user admin --password \!cisco123 --smu_filename n9000-dk9.6.1.2.I3.1.CSCur02700.bin --action status
Inactive Packages:
Active Packages:
Committed Packages:
Tue Jan 27 09:16:50 2015
Install operation 185 by user  admin  at Tue Jan 27 09:16:46 2015
Install remove n9000-dk9.6.1.2.I3.1.CSCur02700.bin
Install operation 185 completed successfully at Tue Jan 27 09:16:46 2015

End of Examples
"""


import argparse
import sys
from cli import *


class Args(object):
    def __init__(self, args): 
        self.tftp_address = args.tftp_address
        self.smu_filename = args.smu_filename
        self.action = args.action

def exe_cmd(cmd_str):
    print cmd_str
    return_xml = clip(cmd_str)
    print return_xml

def copy_patch_file(params):

    cmd_str = 'copy tftp://'
    cmd_str += params.tftp_address
    cmd_str += '/'
    cmd_str += params.smu_filename
    cmd_str += ' bootflash:// vrf management'
    exe_cmd(cmd_str)

def list_patch_file(params):
    cmd_str = 'dir  bootflash:'
    cmd_str += params.smu_filename
    exe_cmd(cmd_str)

def add_module(params):
    cmd_str = 'install add bootflash:' 
    cmd_str += params.smu_filename
    exe_cmd(cmd_str)

def list_inactive_modules():
    cmd_str = 'show install inactive'
    exe_cmd(cmd_str)

def activate_patch_file(params):
    cmd_str = 'install activate ' 
    cmd_str += params.smu_filename
    exe_cmd(cmd_str)

def commit_active_patch_file(params):
    cmd_str = 'install commit '
    cmd_str += params.smu_filename
    exe_cmd(cmd_str)

def commit_inactive_patch_file(params):
    cmd_str = 'install commit '
    cmd_str += params.smu_filename
    exe_cmd(cmd_str)

def list_modules_status():
#    print 'show install inactive'
    exe_cmd('show install inactive')

#    print 'show install active'
    exe_cmd('show install active')

#    print 'show install committed'
    exe_cmd('show install committed')
    
def list_active_modules():
    exe_cmd('show install active')

def deactivate_patch_file(params):
    exe_cmd('install deactivate ' + params.smu_filename)
 
def remove_modules(params):
    exe_cmd('install remove ' + params.smu_filename + ' forced')

def show_install_log():
    exe_cmd('show install log last')

def initialize_args():

        parser = argparse.ArgumentParser(
              description='Nexus 9000 OS software patch management utility.',
              epilog="""to openstack cluster.""")

        parser.add_argument('--tftp_address', '-a', dest='tftp_address',
            help='Tftp server ip-address.')
        parser.add_argument('--smu_filename', '-f', dest='smu_filename',
            help='SMU filename.', required=True)
        parser.add_argument('--action''-o', dest='action',
            help='Action Install/Remove patch file.', required=True,
            choices = ['copy', 'activate', 'deactivate', 'commit_active', 'commit_inactive', 'remove''status'])
        args = parser.parse_args()
        return Args(args)


if __name__ == '__main__':

    params = initialize_args()

    if params.action == 'copy':
        if not params.tftp_address:
            params.tftp_address = raw_input('tftp server address:')
        copy_patch_file(params)
        list_patch_file(params)
    elif params.action == 'activate':
        add_module(params)
        list_inactive_modules()
        activate_patch_file(params)
        list_active_modules()
    elif params.action == 'deactivate':
        list_active_modules()
        deactivate_patch_file(params)
        list_inactive_modules()
    elif params.action == 'remove':
        list_inactive_modules()
        remove_modules(params)
    elif params.action == 'commit_active':
        list_active_modules()
        commit_active_patch_file(params)
    elif params.action == 'commit_inactive':
        list_inactive_modules()
        commit_inactive_patch_file(params)
    elif params.action == 'status':
        list_modules_status()
    show_install_log()
    exit(0)
