"""NDB and device Migration"""
import json
import re
import sys
import time
import logging
import os
import copy
import threading
from threading import Thread
from datetime import datetime
from collections import OrderedDict
import yaml
import paramiko
import requests
from Exscript import Account
from Exscript.protocols import SSH2
from configobj import ConfigObj
import Migrate
import pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ThreadWithReturnValue(Thread):
    """Class Thread overrided to return object"""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return

class NDBMigration(object):
    """Class NDBMigration"""
    def __init__(self, input_path=None):
        self.input_path = input_path
        self.max_thread = 10
        self.rerun_flag = 0
        self.migrate_state = OrderedDict()
        self.date_time = datetime.now().strftime("%Y%b%d_%H:%M:%S")
        self.backup_file = None
        if self.input_path != None:
            pass
        else:
            self.input_path = "Utilities/inputfile.yaml"
        if os.path.exists(self.input_path):
            pass
        else:
            print "Please provide valid input file path"
            sys.exit()
        try:
            with open(self.input_path) as fileobj:
                self.input_dict = yaml.safe_load(fileobj) or {}
        except yaml.YAMLError as exc:
            print('Error parsing file {filename}: {exc}. Please fix and try '
                  'again.'.format(filename=self.input_path, exc=exc))
            sys.exit()
        if len(self.input_dict) == 0:
            print "Input yaml file looks to be empty. So exiting.."
            sys.exit()
        if 'revertFlag' in self.input_dict.keys():
            self.revert_flag = self.input_dict['revertFlag']
        else:
            self.revert_flag = 0
        self.job_id = 'job.'+ self.date_time
        if 'jobPath' not in self.input_dict.keys():
            self.job_path = os.path.dirname(os.path.realpath(__file__)) + '/' + self.job_id
        else:
            self.job_path = input_dict['jobPath'] + '/' + self.job_id
        self.log_path = self.job_path + '/Log'
        self.backup_path = self.job_path + '/Backup'
        self.report_path = self.job_path + '/Report'
        self.devices_dict = self.input_dict['DEVICES']
        self.num_of_devices = len(self.devices_dict)
        if not os.path.isdir(self.backup_path):
            os.makedirs(self.backup_path)
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
            self.logfile = os.path.join(self.log_path
                                        , 'NDBMigrationToolLog.log')
        else:
            self.logfile = os.path.join(self.log_path
                                        , 'NDBMigrationToolLog.log')
        self.statefile = os.path.join(self.job_path, 'Backup/statefile'
                                      + str(self.date_time) + '.json')
        self.statefile_obj = open(self.statefile, 'w')
        with open("Utilities/platformHardwareMap.yaml") as fileobj1:
            self.mapping_dict = yaml.safe_load(fileobj1) or {}
        self.config_dict = copy.deepcopy(self.mapping_dict['NDB_CLEANUP_CONFIGS'])

        if not os.path.isdir(self.report_path):
            os.makedirs(self.report_path)
            self.reportfile = os.path.join(self.report_path,
                                           'NDBMigrationReport_'+ str(self.date_time) + '.log')
        else:
            self.reportfile = os.path.join(self.report_path,
                                           'NDBMigrationReport_'+ str(self.date_time) + '.log')
        with open(self.reportfile, "a") as self.filepointer:
            self.filepointer.write(
                "\t\t*******************************************************\n")
            self.filepointer.write(
                "\t\tNDB MIGRATION GENERATED REPORT                         \n")
            self.filepointer.write(
                "\t\t*******************************************************\n")

        if 'NDBserverIP' in self.input_dict.keys():
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            config_path = self.dir_path + '/Utilities/ndbUrl.cfg'
            self.variable = ConfigObj(config_path)
            self.conn_type = self.variable['connection_type']
            self.port = '8443'
            self.login_payload = {}
            self.server_ip = self.input_dict['NDBserverIP']['host_name/IP']
            self.server_username = self.input_dict['NDBserverIP']['username']
            self.server_pwd = self.input_dict['NDBserverIP']['password']
            self.server_oldpath = self.input_dict['NDBserverIP']['old_path_ndb_build']
            self.server_newpath = self.input_dict['NDBserverIP']['new_path_ndb_build']
            self.login_payload['j_username'] = self.input_dict['NDBserverIP']['ndb_gui_username']
            self.login_payload['j_password'] = self.input_dict['NDBserverIP']['ndb_gui_password']
        else:
            logger.error("NDB server details are not provided")
            sys.exit(0)
        self.old_ndbversion = None
        self.new_ndbversion = None
        self.web_url = (self.conn_type + "://"+str(self.server_ip) + ":" + str(self.port)
                        + self.variable['web_url'])
        self.login_url = (self.conn_type + "://"+str(self.server_ip) + ":" + str(self.port)
                          + self.variable['login_url'])
        self.save_url = (self.conn_type + "://" + self.server_ip + ":"
                         + self.port + self.variable['save_url'])
        self.download_url = (self.conn_type + "://" + self.server_ip + ":"
                             +self.port+self.variable['download_url'])
        self.get_connections_url = (self.conn_type + "://" + self.server_ip + ":"
                                    + self.port+self.variable['get_connection_url'])
        self.get_devices_url = (self.conn_type + "://" + self.server_ip + ":"
                                +self.port+self.variable['get_device_url'])
        self.get_filters_url = (self.conn_type + "://" + self.server_ip + ":"
                                +self.port+self.variable['get_filters_url'])
        self.get_ports_url = (self.conn_type + "://" + self.server_ip + ":"
                              +self.port+self.variable['get_ports_url'])
        self.import_url = (self.conn_type + "://" + self.server_ip + ":"
                           + self.port + self.variable['import_url'])
        self.get_admin_url = (self.conn_type + "://" + self.server_ip + ":"
                              + self.port)
        self.import_apply_url = (self.conn_type + "://" + self.server_ip + ":"
                                 + self.port+self.variable['import_apply_url'])
        self.import_continue_url = (self.conn_type + "://" + self.server_ip + ":"
                                    + self.port+self.variable['import_continue_url'])
        self.upload_url = (self.conn_type + "://" + self.server_ip + ":"
                           +self.port+self.variable['upload_url'])
        self.export_get_url = (self.conn_type + "://" + self.server_ip + ":"
                               + self.port + self.variable['export_url'])

    def ndb_migrate(self, job_id=''):
        """Invokes other methods to perform migration"""
        try:
            if job_id != '':
                self.rerun_flag = 1
                if job_id.endswith('/'):
                    read_file = (self.dir_path + '/' + job_id + 'Backup/statefile'
                                 + job_id.strip('job.''/') + '.json')
                else:
                    read_file = (self.dir_path + '/' + job_id + '/Backup/statefile'
                                 + job_id.strip('job.') + '.json')
                with open(read_file, 'r+') as read_file_obj:
                    self.migrate_state = json.load(read_file_obj, object_pairs_hook=OrderedDict)
                date_time = job_id.split('.')[1]
                if 'backup_file' in self.input_dict.keys():
                    self.backup_file = self.input_dict['backup_file'] + date_time
                else:
                    self.backup_file = "Migration_backup_" + date_time
            else:
                get_runtime(self.devices_dict)
                if 'backup_file' in self.input_dict.keys():
                    self.backup_file = self.input_dict['backup_file'] + self.date_time
                else:
                    self.backup_file = "Migration_backup_" + self.date_time
            logger.info("Job Id of current run - %s", self.job_id)
            state_items = self.migrate_state.keys()
            if ('migration_status' in state_items
                    and self.migrate_state['migration_status'] == "PASS"):
                logger.info("NDB Migration completed successfully")
                self.update_state()
                sys.exit()
            if 'revert_status' in state_items and self.migrate_state['revert_status'] == "PASS":
                logger.info("Previous run state had successful revert. "
                            "Please initiate an new run..")
                self.update_state()
                sys.exit()
            dev_list = []
            for item in self.devices_dict.keys():
                dev_list.append(self.devices_dict[item]['host_name/IP'])
            logger.info("Migrating device details - %s", dev_list)
            #if 'revert_device_conversion' not in state_items:
            if self.rerun_flag == 0:
                logger.info("Checking for input parameters provided in input file")
                validate_flag = self.validate_inputfile()
                if not validate_flag:
                    logger.error("Input file validation failed. Exiting..")
                    sys.exit()
            self.old_ndbversion = self.get_ndbversion(self.server_oldpath)
            self.new_ndbversion = self.get_ndbversion(self.server_newpath)
            if 'ndb_upgrade' not in state_items or self.migrate_state['ndb_upgrade'] == 'FAIL':
                if not self.rerun_flag:
                    logger.info("Getting the devices and connections info before upgrade")
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t**********************************************\n")
                        self.filepointer.write(
                            "\t\tCONFIGURATIONS PRESENT IN NDB BEFORE MIGRATION\n")
                        self.filepointer.write(
                            "\t\t**********************************************\n")
                    self.get_ndb_data(self.old_ndbversion)
                if self.old_ndbversion > self.new_ndbversion:
                    logger.info("Migration not supported for NDB from %s to %s",
                                self.old_ndbversion, self.new_ndbversion)
                    self.migrate_state['ndb_upgrade'] = 'NA'
                    self.update_state()
                elif self.old_ndbversion == self.new_ndbversion:
                    logger.info("No need to upgrade the NDB as current NDB \
                    version is already NDB %s", self.new_ndbversion)
                    self.migrate_state['ndb_upgrade'] = 'NA'
                    self.update_state()
                else:
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\tSTEP 1: UPGRADE TO NDB " + self.new_ndbversion + "\n")
                        self.filepointer.write(
                            "\t\t*************************************************\n")
                    upgrade_response = self.ndb_upgrade()
                    if not upgrade_response:
                        logger.error("NDB upgrade failed. Reverting back to %s NDB configuration",
                                     self.old_ndbversion)
                        self.migrate_state['ndb_upgrade'] = 'FAIL'
                        self.update_state()
                        if self.ndb_revert():
                            self.migrate_state['ndb_revert'] = 'PASS'
                        else:
                            self.migrate_state['ndb_revert'] = 'FAIL'
                        self.update_state()
                        with open(self.reportfile, "a") as self.filepointer:
                            self.filepointer.write(
                                "\t\t UPGRADE STATUS : Fail \n\n")
                        sys.exit()
                    else:
                        logger.info("NDB upgrade to %s was successful", self.new_ndbversion)
                        self.migrate_state['ndb_upgrade'] = 'PASS'
                        self.update_state()
                        with open(self.reportfile, "a") as self.filepointer:
                            self.filepointer.write(
                                "\t\t UPGRADE STATUS : Pass \n\n")
            if 'ndb_export' not in state_items or self.migrate_state['ndb_export'] == 'FAIL':
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\tSTEP 2: EXPORT NDB CONFIGURATIONS IN " + self.new_ndbversion + "\n")
                    self.filepointer.write(
                        "\t\t****************************************************************\n")
                export_response = self.ndb_export()
                if not export_response:
                    logger.error("NDB export failed. Reverting back to %s NDB configuration",
                                 self.old_ndbversion)
                    self.migrate_state['ndb_export'] = 'FAIL'
                    self.update_state()
                    if self.ndb_revert():
                        self.migrate_state['ndb_revert'] = 'PASS'
                    else:
                        self.migrate_state['ndb_revert'] = 'FAIL'
                    self.update_state()
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t EXPORT STATUS : Fail \n\n")
                    sys.exit()
                else:
                    logger.info("Export of NDB configurations in NDB %s was successful",
                                self.new_ndbversion)
                    self.migrate_state['ndb_export'] = 'PASS'
                    self.update_state()
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t EXPORT STATUS : Pass \n\n")
            if 'ndb_cleanup' not in state_items or self.migrate_state['ndb_cleanup'] == 'FAIL':
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\tSTEP 3: CLEAN UP NDB CONFIGS IN" + self.new_ndbversion + "\n")
                    self.filepointer.write(
                        "\t\t********************************************************\n")
                cleanndb = self.clean_ndb_config(self.server_newpath)
                if not cleanndb:
                    logger.error("NDB cleanup failed. Reverting back to %s NDB configuration",
                                 self.old_ndbversion)
                    self.migrate_state['ndb_cleanup'] = 'FAIL'
                    self.update_state()
                    if self.ndb_revert():
                        self.migrate_state['ndb_revert'] = 'PASS'
                    else:
                        self.migrate_state['ndb_revert'] = 'FAIL'
                    self.update_state()
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t NDB CLEANUP : Fail \n\n")
                    sys.exit()
                else:
                    logger.info("Cleanup of NDB configurations in NDB %s was successful",
                                self.new_ndbversion)
                    self.migrate_state['ndb_cleanup'] = 'PASS'
                    self.update_state()
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t NDB CLEANUP : Pass \n\n")
            # Add the check for downgrading
            downgradable_device_flag = 0
            if ("device_downgrade" in state_items
                    and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'FAIL'
                    and self.revert_flag):
                downgradable_device_flag = 1
                devices_failed_list = []
                for key in self.migrate_state['device_downgrade'].keys():
                    if ("device_downgrade_status" in key
                            and len(self.migrate_state['device_downgrade'].keys()) == 1):
                        devices_failed_list = self.devices_dict.keys()
                    elif "device_downgrade_status" in key:
                        pass
                    elif (self.migrate_state['device_downgrade'][
                            key]['overall_status'] == "FAIL"):
                        for key1 in self.devices_dict.keys():
                            if (self.devices_dict[key1]['host_name/IP'] == key
                                    and "NXOS_Image1" in self.migrate_state['device_upgrade'][key].keys()
                                    and "upgrade_status" in self.migrate_state['device_upgrade'][key]['NXOS_Image1'].keys()
                                    and self.migrate_state['device_upgrade'][key]['NXOS_Image1']['upgrade_status'] == 'PASS'):
                                devices_failed_list.append(key1)
                if len(devices_failed_list) > 0:
                    logger.info("Rerunning the dowgrade process for failed devices")
                    nxos_revert_flag = self.downgrade_nxos(self.max_thread, devices_failed_list)
                    self.update_state()
                else:
                    logger.info("Devices are already loaded with older nx-os images")
                    self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS'
                    self.update_state()
            if ("revert_device_conversion" in state_items
                    and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'FAIL'
                    and self.revert_flag):
                devices_failed_list = []
                for key in self.migrate_state['revert_device_conversion'].keys():
                    if ("revert_device_conversion_status" in key
                            and len(self.migrate_state['revert_device_conversion'].keys()) == 1):
                        devices_failed_list = self.devices_dict.keys()
                    elif "revert_device_conversion_status" in key:
                        pass
                    elif (self.migrate_state['revert_device_conversion'][
                            key]['overall_status'] == "FAIL"):
                        for key1 in self.devices_dict.keys():
                            if self.devices_dict[key1]['host_name/IP'] == key:
                                devices_failed_list.append(key1)
                if len(devices_failed_list) != 0:
                    for failed_item in devices_failed_list:
                        ipaddr = self.devices_dict[failed_item]['host_name/IP']
                        if 'package_name' in self.migrate_state['device_conversion'][ipaddr]:
                            self.devices_dict[failed_item]['pkg_name'] = copy.deepcopy(
                                self.migrate_state['device_conversion'][ipaddr]['package_name'])
                logger.info("Rerunning the revert device conversion proc for failed devices")
                dev_revert_flag = self.revert_device_configs(self.max_thread, devices_failed_list)
                self.update_state()
                if ('ndb_revert' in state_items and self.migrate_state['ndb_revert'] == 'FAIL') or 'ndb_revert' not in state_items:
                    ndb_revert_flag = self.ndb_revert()
                    if not ndb_revert_flag:
                        self.migrate_state['ndb_revert'] = 'FAIL'
                    else:
                        self.migrate_state['ndb_revert'] = 'PASS'
                    self.update_state()
                    
                if self.migrate_state['ndb_revert'] == 'PASS' and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'PASS':
                    if (downgradable_device_flag == 1 and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS') or downgradable_device_flag == 0:
                        logger.info("All devices and NDB %s are reverted back successfully", self.old_ndbversion)
                        self.migrate_state['revert_status'] = 'PASS'
                sys.exit()
            elif ('device_conversion' not in state_items
                  or self.migrate_state['device_conversion']['device_conversion_status'] == 'FAIL'):
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\tSTEP 4: DEVICE CONVERSION FROM OF TO NXAPI \n")
                    self.filepointer.write(
                        "\t\t******************************************\n")
                if 'device_conversion' in self.migrate_state.keys():
                    if self.migrate_state['device_conversion']['device_conversion_status'] == "FAIL":
                        logger.info("This is rerun for failed devices")
                        devices_failed_list = []
                        for key in self.migrate_state['device_conversion'].keys():
                            if "device_conversion_status" in key:
                                continue
                            if (self.migrate_state['device_conversion'][
                                    key]['overall_status'] == "FAIL"):
                                for key1 in self.devices_dict.keys():
                                    if self.devices_dict[key1]['host_name/IP'] == key:
                                        devices_failed_list.append(key1)
                        logger.info("Rerunning the device conversion proc for failed devices")
                        convertdevice = self.convert_of_nxapi(self.max_thread, devices_failed_list)
                else:
                    convertdevice = self.convert_of_nxapi(self.max_thread,
                                                          self.devices_dict.keys())
                if convertdevice:
                    self.update_state()
                    self.migrate_state['device_conversion']['device_conversion_status'] = "PASS"
                    for key in self.migrate_state['device_conversion'].keys():
                        if "device_conversion_status" in key:
                            continue
                        if "FAIL" in self.migrate_state['device_conversion'][key].values():
                            self.migrate_state['device_conversion'][key]['overall_status'] = "FAIL"
                            self.migrate_state['device_conversion']['device_conversion_status'] = "FAIL"
                        else:
                            self.migrate_state['device_conversion'][key]['overall_status'] = "PASS"
                    if self.revert_flag:
                        logger.info("Reverting back all openflow configuration in devices")
                        dev_revert_falg = self.revert_device_configs(self.max_thread,
                                                                     self.devices_dict.keys())
                        logger.error("Device conversion failed. Reverting back to %s NDB "
                                     "configuration", self.old_ndbversion)
                        ndb_revert_flag = self.ndb_revert()
                        if ('ndb_revert' in state_items and self.migrate_state['ndb_revert'] == 'FAIL') or 'ndb_revert' not in state_items:
                            if not ndb_revert_flag:
                                self.migrate_state['ndb_revert'] = 'FAIL'
                            else:
                                self.migrate_state['ndb_revert'] = 'PASS'
                            self.update_state()
                        with open(self.reportfile, "a") as self.filepointer:
                            self.filepointer.write(
                                "\t\t DEVICE CONVERSION : Fail \n\n")
                        sys.exit()
                    else:
                        self.update_state()
                        with open(self.reportfile, "a") as self.filepointer:
                            self.filepointer.write(
                                "\t\t DEVICE CONVERSION : Fail \n\n")
                else:
                    logger.info("NXAPI conversion for all devices were successful")
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t DEVICE CONVERSION : Pass \n\n")
                    self.migrate_state['device_conversion']['device_conversion_status'] = "PASS"
                    for key in self.migrate_state['device_conversion'].keys():
                        if "device_conversion_status" in key:
                            continue
                        if "FAIL" in self.migrate_state['device_conversion'][key].values():
                            self.migrate_state['device_conversion'][key]['overall_status'] = "FAIL"
                            self.migrate_state['device_conversion']['device_conversion_status'] = "FAIL"
                        else:
                            self.migrate_state['device_conversion'][key]['overall_status'] = "PASS"
                    self.update_state()
            else:
                if 'revert_device_conversion' in state_items:
                    logger.info("Revert device conversion performed already on all devices")
                    self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] = "PASS"
                    sys.exit()
                else:
                    logger.info("Device conversion was already done on all devices")
                    self.migrate_state['device_conversion']['device_conversion_status'] = "PASS"
            upgradable_devices = []
            downgradable_devices = []
            upgrade_device = None
            if self.rerun_flag == 0:
                for dev_item in self.devices_dict:
                    if any('NXOS_Image' in substring for substring
                           in self.devices_dict[dev_item].keys()):
                        upgradable_devices.append(dev_item)
                if len(upgradable_devices) != 0:
                    upgrade_device, self.migrate_state = self.upgrade_nxos(self.max_thread,
                                                                           upgradable_devices)
                else:
                    self.migrate_state['device_upgrade'] = OrderedDict()
                    self.migrate_state['device_upgrade']['device_upgrade_status'] = 'SKIP'
                self.update_state()
                for key in self.devices_dict.keys():
                    ip_addr = copy.deepcopy(self.devices_dict[key]['host_name/IP'])
                    if (ip_addr in self.migrate_state['device_upgrade'].keys()
                            and "NXOS_Image1" in self.migrate_state['device_upgrade'][ip_addr].keys()
                            and "upgrade_status" in self.migrate_state['device_upgrade'][ip_addr]['NXOS_Image1'].keys()
                            and self.migrate_state['device_upgrade'][ip_addr]['NXOS_Image1']['upgrade_status'] == 'PASS'):
                        downgradable_devices.append(key)
                if upgrade_device and self.revert_flag == 1:
                    if len(downgradable_devices) > 0:
                        logger.info("Reverting all switches with older images")
                        nxos_revert_flag = self.downgrade_nxos(self.max_thread, downgradable_devices)
                        self.update_state()
                    else:
                        logger.info("Devices are already loaded with older nx-os images")
                        self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS'
                        self.update_state()
                    logger.info("Reverting back all openflow configuration in devices")
                    dev_revert_falg = self.revert_device_configs(self.max_thread,
                                                                 self.devices_dict.keys())
                    self.update_state()
                    if ('ndb_revert' in state_items and self.migrate_state['ndb_revert'] == 'FAIL') or 'ndb_revert' not in state_items:
                        ndb_revert_flag = self.ndb_revert()
                        if not ndb_revert_flag:
                            self.migrate_state['ndb_revert'] = 'FAIL'
                        else:
                            self.migrate_state['ndb_revert'] = 'PASS'
                        self.update_state()
                    if (self.migrate_state['ndb_revert'] == 'PASS'
                            and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'PASS'):
                        if ('device_downgrade' in state_items and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS') or 'device_downgrade' not in state_items:
                            logger.info("All devices and NDB %s are reverted back successfully", self.old_ndbversion)
                            self.migrate_state['revert_status'] = 'PASS'
                    sys.exit()
                elif upgrade_device and self.revert_flag == 0:
                    logger.error("Upgrade failed")
            elif self.rerun_flag == 1:
                trigger_upgrade_flag = 0
                if "device_downgrade" in self.migrate_state.keys():
                    pass
                elif ("device_upgrade" not in self.migrate_state.keys()
                      or ("device_upgrade" in self.migrate_state.keys()
                      and self.migrate_state['device_upgrade']['device_upgrade_status'] == 'FAIL')):
                    trigger_upgrade_flag = 1
                else:
                    pass
                if trigger_upgrade_flag == 1:
                    for dev_item in self.devices_dict:
                        if any('NXOS_Image' in substring for substring
                               in self.devices_dict[dev_item].keys()):
                            ip_addr = self.devices_dict[dev_item]['host_name/IP']
                            if (ip_addr in self.migrate_state['device_upgrade'].keys()
                                    and self.migrate_state['device_upgrade'][
                                        ip_addr]['overall_status'] == 'FAIL'):
                                upgradable_devices.append(dev_item)
                    if len(upgradable_devices) != 0:
                        upgrade_device, self.migrate_state = self.upgrade_nxos(self.max_thread,
                                                                               upgradable_devices)
                    else:
                        self.migrate_state['device_upgrade'] = OrderedDict()
                        self.migrate_state['device_upgrade']['device_upgrade_status'] = 'SKIP'
                    self.update_state()
                if self.revert_flag == 1:
                    for dev_item in self.devices_dict:
                        ip_addr = self.devices_dict[dev_item]['host_name/IP']
                        if ('switch_image' in self.migrate_state["device_downgrade"][
                                ip_addr].keys()):
                            self.devices_dict[dev_item]["switch_image"] = copy.deepcopy(
                                self.migrate_state["device_downgrade"][ip_addr]['switch_image'])
                    if 'device_downgrade' not in self.migrate_state.keys():
                        for dev_item in self.devices_dict:
                            if any('NXOS_Image' in substring for substring
                                   in self.devices_dict[dev_item].keys()):
                                downgradable_devices.append(dev_item)
                    elif ('device_downgrade' in self.migrate_state.keys()
                          and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'FAIL'):
                        for dev_item in self.devices_dict:
                            if any('NXOS_Image' in substring for substring
                                   in self.devices_dict[dev_item].keys()):
                                ip_addr = self.devices_dict[dev_item]['host_name/IP']
                                if (dev_item not in self.migrate_state['device_downgrade'].keys()
                                        or self.migrate_state['device_downgrade'][
                                            ip_addr]['overall_status'] == 'FAIL'):
                                    downgradable_devices.append(dev_item)
                    if len(downgradable_devices) != 0:
                        downgrade_device = self.downgrade_nxos(self.max_thread,
                                                               downgradable_devices)
                        if not downgrade_device:
                            self.migrate_state['device_downgrade']['device_downgrade_status'] = 'FAIL'
                        elif downgrade_device:
                            self.migrate_state['device_downgrade']['device_downgrade_status'] = 'PASS'
                    else:
                        self.migrate_state['device_downgrade']['device_downgrade_status'] = 'SKIP'
                        self.update_state()
                    logger.info("Reverting back all openflow configuration in devices")
                    dev_revert_falg = self.revert_device_configs(self.max_thread,
                                                                 self.devices_dict.keys())
                    self.update_state()
                    if 'ndb_revert' in state_items and self.migrate_state['ndb_revert'] == 'FAIL':
                        ndb_revert_flag = self.ndb_revert()
                        if not ndb_revert_flag:
                            self.migrate_state['ndb_revert'] = 'FAIL'
                        else:
                            self.migrate_state['ndb_revert'] = 'PASS'
                        self.update_state()
                    if (self.migrate_state['ndb_revert'] == 'PASS'
                            and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'PASS'
                            and ('device_downgrade' in state_items and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS')):
                        logger.info("All devices and NDB %s are reverted back successfully", self.old_ndbversion)
                        self.migrate_state['revert_status'] = 'PASS'
                    sys.exit()
            if ('ndb_import' not in state_items
                    or self.migrate_state['ndb_import']['ndb_import_status'] == 'FAIL'):
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\tSTEP 5: IMPORT NDB CONFIGS INTO NDB"+ self.new_ndbversion + "\n")
                    self.filepointer.write(
                        "\t\t*************************************************************\n")
                if self.rerun_flag == 1 or 'ndb_import' in self.migrate_state.keys():
                    if (self.migrate_state['ndb_import']['ndb_import_status'] == 'FAIL'
                            or self.rerun_flag == 1):
                        logger.info("Import rerun")
                        import_rerunflag = 1
                        jobpath = os.path.dirname(os.path.realpath(__file__)) + '/' + job_id
                else:
                    jobpath = self.job_path
                    import_rerunflag = 0
                import_flag = self.ndb_import(jobpath, import_rerunflag)
                if not import_flag:
                    self.update_state()
                    if self.revert_flag:
                        device_failed_list = []
                        for key in self.devices_dict.keys():
                            ip_addr = copy.deepcopy(self.devices_dict[key]['host_name/IP'])
                            if (ip_addr in self.migrate_state['device_upgrade'].keys()
                                    and "NXOS_Image1" in self.migrate_state['device_upgrade'][ip_addr].keys()
                                    and "upgrade_status" in self.migrate_state['device_upgrade'][ip_addr]['NXOS_Image1'].keys()
                                    and self.migrate_state['device_upgrade'][ip_addr]['NXOS_Image1']['upgrade_status'] == 'PASS'):
                                device_failed_list.append(key)
                        if len(device_failed_list) > 0:
                            logger.info("Reverting all switches with older images")
                            nxos_revert_flag = self.downgrade_nxos(self.max_thread, device_failed_list)
                            self.update_state()
                        else:
                            logger.info("Devices are already loaded with older nx-os images")
                            self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS'
                            self.update_state()
                        logger.info("Reverting back all openflow configuration in devices")
                        dev_revert_falg = self.revert_device_configs(self.max_thread, self.devices_dict.keys())
                        logger.error("NDB import failed. Reverting back to %s NDB configuration",
                                     self.old_ndbversion)
                        if ('ndb_revert' in state_items and self.migrate_state['ndb_revert'] == 'FAIL') or 'ndb_revert' not in state_items:
                            ndb_revert_flag = self.ndb_revert()
                            if not ndb_revert_flag:
                                self.migrate_state['ndb_revert'] = 'FAIL'
                            else:
                                self.migrate_state['ndb_revert'] = 'PASS'
                            self.update_state()
                        if (self.migrate_state['ndb_revert'] == 'PASS'
                                and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'PASS'):
                            if ('device_downgrade' in state_items and self.migrate_state['device_downgrade']['device_downgrade_status'] == 'PASS') or 'device_downgrade' not in state_items:
                                logger.info("All devices and NDB %s are reverted back successfully", self.old_ndbversion)
                                self.migrate_state['revert_status'] = 'PASS'
                        sys.exit()
                    logger.error("NDB import failed")
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t IMPORT STATUS : Fail \n\n")
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t MIGRATION STATUS : Fail \n")
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t**********************************************\n")
                        self.filepointer.write(
                            "\t\tCONFIGURATIONS PRESENT IN NDB AFTER MIGRATION\n")
                        self.filepointer.write(
                            "\t\t**********************************************\n")
                    self.get_ndb_data(self.new_ndbversion)
                    sys.exit()
                else:
                    logger.info("Import of NDB configurations in NDB %s was successful",
                                self.new_ndbversion)
                    self.update_state()
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\t\t IMPORT STATUS : Pass \n\n")
                logger.info("Getting the devices and connections info after successful migration")
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\t**********************************************\n")
                    self.filepointer.write(
                        "\t\tCONFIGURATIONS PRESENT IN NDB AFTER MIGRATION\n")
                    self.filepointer.write(
                        "\t\t**********************************************\n")
                self.get_ndb_data(self.new_ndbversion)
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\t MIGRATION STATUS : Pass \n")
            self.migrate_state['migration_status'] = 'PASS'
            for key, value in self.migrate_state.iteritems():
                key_check1 = ['ndb_upgrade', 'ndb_cleanup', 'ndb_export']
                key_check2 = ['device_upgrade', 'device_conversion', 'ndb_import']
                key_status = key + '_status'
                if ((key in key_check1 and value == 'FAIL') or (key in key_check2
                        and self.migrate_state[key][key_status] == 'FAIL')):
                    self.migrate_state['migration_status'] = 'FAIL'
            self.update_state()
            if 'migration_status' in self.migrate_state.keys() and self.migrate_state['migration_status'] == 'PASS':
                logger.info("NDB migration from %s to NDB %s was successful",
                            self.old_ndbversion, self.new_ndbversion)
            else:
                logger.info("NDB migration from %s to NDB %s was not successful",
                            self.old_ndbversion, self.new_ndbversion)
        except paramiko.AuthenticationException:
            logger.error("User credentials of NDB given in inputfile are wrong. Pls check")

        except Exception as content:
            logger.error("%s", content)

    def validate_inputfile(self):
        """Validating input file"""
        try:
            support_flag = 1
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.server_ip, port=22, username=self.server_username, password=self.server_pwd)
            oldndb_path = 'cd '+ self.server_oldpath
            _, _, stderr = ssh.exec_command(oldndb_path)
            if stderr.read() != '':
                logger.error("NDB paths provided in inputfile do not exist")
                support_flag = 0
                return support_flag
            newndb_path = 'cd '+ self.server_newpath
            _, _, stderr = ssh.exec_command(newndb_path)
            if stderr.read() != '':
                logger.error("NDB paths provided in inputfile do not exist")
                support_flag = 0
                return support_flag
            support_flag = check_device_support(self.devices_dict, self.rerun_flag, self.backup_file)
            return support_flag
        except Exception as content:
            logger.error("%s", content)
            return 0

    def update_state(self):
        try:
            self.statefile_obj.close()
            file_name = self.statefile_obj.name
            self.statefile_obj = open(file_name, 'w')                                               
            json.dump(self.migrate_state, self.statefile_obj)
        except:
            logger.error("Error while dumping states to a %s", self.statefile)

    def get_ndbversion(self, ndb_path):
        """Get NDB version"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.server_ip, port=22, username=self.server_username, password=self.server_pwd)
            cat_properties = ('cd ' + ndb_path
                              + ' \n cat version.properties '
                              + '| grep "com.cisco.csdn.monitor.application.version"')
            _, stdout, _ = ssh.exec_command(cat_properties)
            count = 0
            while not stdout.channel.eof_received:
                time.sleep(1)
                count = count + 1
                if stdout.channel.eof_received or count > 10:
                    break
            console = stdout.read()
            contents = console.strip()
            version = contents.split('=')[1]
            return version

        except Exception as content:
            logger.error("%s", content)

    def convert_of_nxapi(self, max_thread, devices_list):
        """Converting all openflow devices to NXAPI"""
        try:
            with open("Utilities/platformHardwareMap.yaml") as fileobj1:
                hardware_dict = yaml.safe_load(fileobj1)
            threading_devices = {}
            lock = threading.Lock()
            for dev_item in devices_list:
                threading_devices[dev_item] = ThreadWithReturnValue(
                    target=Migrate.openflow_to_nxapi,
                    args=(self.devices_dict[dev_item], hardware_dict, lock, self.migrate_state, self.backup_file),
                    name=self.devices_dict[dev_item]['host_name/IP']
                )
            dev_key = devices_list
            count = 1
            start_position = 1
            join_position = 1
            while count <= len(dev_key):
                if len(dev_key) - count >= max_thread:
                    logger.info("Performing NX-API conversion on these switches %s",
                                dev_key[count-1:count+(max_thread-1)])
                else:
                    logger.info("Performing NX-API conversion on these switches %s",
                                dev_key[count-1:])
                while True:
                    if start_position % max_thread == 0 or start_position == len(dev_key):
                        thread_item = dev_key[start_position-1]
                        threading_devices[thread_item].start()
                        start_position += 1
                        break
                    thread_item = dev_key[start_position-1]
                    threading_devices[thread_item].start()
                    start_position += 1
                while True:
                    if join_position % max_thread == 0 or join_position == len(dev_key):
                        thread_item = dev_key[join_position-1]
                        self.devices_dict[thread_item], self.migrate_state = threading_devices[
                            thread_item].join()
                        join_position += 1
                        count += 1
                        break
                    thread_item = dev_key[join_position-1]
                    self.devices_dict[thread_item], self.migrate_state = threading_devices[
                        thread_item].join()
                    join_position += 1
                    count += 1
            return Migrate.fail_flag
        except Exception as content:
            logger.error("%s", content)

    def revert_device_configs(self, max_thread, revert_devices):
        """Reverting device with older running configs"""
        try:
            state_file = copy.deepcopy(self.migrate_state)
            threading_devices = {}
            for dev_item in revert_devices:
                threading_devices[dev_item] = ThreadWithReturnValue(
                    target=Migrate.revert_configs,
                    args=(self.devices_dict[dev_item], state_file, self.backup_file),
                    name=self.devices_dict[dev_item]['host_name/IP']
                )
            dev_key = revert_devices
            count = 1
            start_position = 1
            join_position = 1
            while count <= len(dev_key):
                if len(dev_key) - count >= max_thread:
                    logger.info("Reverting to older configuraition in these switches %s",
                                dev_key[count-1:count+(max_thread-1)])
                else:
                    logger.info("Reverting to older configuraition in these switches %s",
                                dev_key[count-1:])
                while True:
                    if start_position % max_thread == 0 or start_position == len(dev_key):
                        thread_item = dev_key[start_position-1]
                        threading_devices[thread_item].start()
                        start_position += 1
                        break
                    thread_item = dev_key[start_position-1]
                    threading_devices[thread_item].start()
                    start_position += 1
                while True:
                    if join_position % max_thread == 0 or join_position == len(dev_key):
                        thread_item = dev_key[join_position-1]
                        self.devices_dict[thread_item], self.migrate_state = threading_devices[
                            thread_item].join()
                        join_position += 1
                        count += 1
                        break
                    thread_item = dev_key[join_position-1]
                    self.devices_dict[thread_item], self.migrate_state = threading_devices[
                        thread_item].join()
                    join_position += 1
                    count += 1
            self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] = 'PASS'
            for key,value in self.migrate_state.iteritems():
                if 'revert_device_conversion' in key:
                    revert_dev_dict = copy.deepcopy(self.migrate_state['revert_device_conversion'])
                    for key1, value1 in revert_dev_dict.iteritems():
                        if 'revert_device_conversion_status' in key1:
                            pass
                        elif revert_dev_dict[key1]['overall_status'] == 'FAIL':
                            self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] = 'FAIL'
                            break
            self.update_state()
            if 'revert_device_conversion' in self.migrate_state.keys():
                if 'revert_device_conversion' in self.migrate_state['revert_device_conversion'].keys() and self.migrate_state['revert_device_conversion']['revert_device_conversion_status'] == 'PASS':
                    return 1
            else:
                return 0
        except Exception as content:
            logger.error("%s", content)
            return 0

    def upgrade_nxos(self, max_thread, upgradable_devices):
        """Converting all openflow devices to NXAPI"""
        self.migrate_state['device_upgrade'] = OrderedDict()
        self.migrate_state['device_upgrade']['device_upgrade_status'] = "FAIL"
        self.update_state()
        try:
            upgradable_devices = upgradable_devices
            threading_devices = {}
            dev_key = []
            for dev_item in upgradable_devices:
                threading_devices[dev_item] = ThreadWithReturnValue(
                    target=Migrate.upgrade_switch, args=(self.devices_dict[dev_item],),
                    name=self.devices_dict[dev_item]['host_name/IP']
                )
                dev_key.append(dev_item)
            count = 1
            start_position = 1
            join_position = 1
            while count <= len(dev_key):
                if len(dev_key) - count >= max_thread:
                    logger.info("Performing switch upgrade based on input in these %s switches",
                                dev_key[count-1:count+(max_thread-1)])
                else:
                    logger.info("Performing switch upgrade based on input in these %s switches",
                                dev_key[count-1:])
                while True:
                    if start_position % max_thread == 0 or start_position == len(dev_key):
                        thread_item = dev_key[start_position-1]
                        threading_devices[thread_item].start()
                        start_position += 1
                        break
                    thread_item = dev_key[start_position-1]
                    threading_devices[thread_item].start()
                    start_position += 1
                while True:
                    if join_position % max_thread == 0 or join_position == len(dev_key):
                        thread_item = dev_key[join_position-1]
                        ip_addr = self.devices_dict[thread_item]['host_name/IP']
                        self.devices_dict[thread_item], self.migrate_state['device_upgrade'][
                            ip_addr] = threading_devices[thread_item].join()
                        join_position += 1
                        count += 1
                        break
                    thread_item = dev_key[join_position-1]
                    ip_addr = self.devices_dict[thread_item]['host_name/IP']
                    self.devices_dict[thread_item], self.migrate_state['device_upgrade'][
                        ip_addr] = threading_devices[thread_item].join()
                    join_position += 1
                    count += 1
            self.update_state()
            self.migrate_state['device_upgrade']['device_upgrade_status'] = "PASS"
            for dev_item in upgradable_devices:
                ip_addr = self.devices_dict[dev_item]['host_name/IP']
                if self.migrate_state['device_upgrade'][ip_addr]['overall_status'] == "FAIL":
                    self.migrate_state['device_upgrade']['device_upgrade_status'] = "FAIL"
                    self.update_state()
                    return True, self.migrate_state
            self.update_state()
            return Migrate.upgrade_fail_flag, self.migrate_state
        except Exception as content:
            logger.error("%s", content)
            return True, self.migrate_state

    def downgrade_nxos(self, max_thread, downgradable_devices):
        """Converting all openflow devices to NXAPI"""
        self.migrate_state['device_downgrade'] = OrderedDict()
        self.migrate_state['device_downgrade']['device_downgrade_status'] = "FAIL"
        self.update_state()
        try:
            threading_devices = {}
            dev_key = []
            for dev_item in downgradable_devices:
                threading_devices[dev_item] = ThreadWithReturnValue(
                    target=Migrate.revert_nxos, args=(self.devices_dict[dev_item],),
                    name=self.devices_dict[dev_item]['host_name/IP']
                )
                dev_key.append(dev_item)
            count = 1
            start_position = 1
            join_position = 1
            while count <= len(dev_key):
                if len(dev_key) - count >= max_thread:
                    logger.info("Reverting switch upgrade based on input in these %s switches",
                                dev_key[count-1:count+(max_thread-1)])
                else:
                    logger.info("Reverting switch upgrade based on input in these %s switches",
                                dev_key[count-1:])
                while True:
                    if start_position % max_thread == 0 or start_position == len(dev_key):
                        thread_item = dev_key[start_position-1]
                        threading_devices[thread_item].start()
                        start_position += 1
                        break
                    thread_item = dev_key[start_position-1]
                    threading_devices[thread_item].start()
                    start_position += 1
                while True:
                    if join_position % max_thread == 0 or join_position == len(dev_key):
                        thread_item = dev_key[join_position-1]
                        ip_addr = self.devices_dict[thread_item]['host_name/IP']
                        self.devices_dict[thread_item], self.migrate_state['device_downgrade'][
                            ip_addr] = threading_devices[thread_item].join()
                        join_position += 1
                        count += 1
                        break
                    thread_item = dev_key[join_position-1]
                    ip_addr = self.devices_dict[thread_item]['host_name/IP']
                    self.devices_dict[thread_item], self.migrate_state['device_downgrade'][
                        ip_addr] = threading_devices[thread_item].join()
                    join_position += 1
                    count += 1
            self.migrate_state['device_downgrade']['device_downgrade_status'] = "PASS"
            for dev_item in downgradable_devices:
                ip_addr = self.devices_dict[dev_item]['host_name/IP']
                if self.migrate_state['device_downgrade'][ip_addr]['overall_status'] == "FAIL":
                    self.migrate_state['device_downgrade']['device_downgrade_status'] = "FAIL"
                    self.update_state()
                    return 0
            self.update_state()
            return 1
        except Exception as content:
            logger.error("%s", content)
            return 0

    def ndb_upgrade(self):
        """Upgrading NDB from older to newer version"""
        try:
            upgradeflag = 1
            startstatus = 0
            ndb_version = self.old_ndbversion
            if ndb_version < "3.2":
                logger.info("Saving the NDB config before download")
                with requests.session() as s_obj:
                    s_obj.get(self.web_url, verify=False)
                    s_obj.post(self.login_url, data=self.login_payload, verify=False)
                    save_response = s_obj.post(self.save_url, verify=False)
                    if save_response.status_code == 200:
                        logger.info("Save successful")
                    else:
                        logger.error("Error while saving the configuration")
                        return 0
            logger.info("Downloading the NDB zip file from current NDB")
            currentndbzipfile = ndb_version + '.zip'
            with requests.session() as s_obj:
                s_obj.get(self.web_url, verify=False)
                s_obj.post(self.login_url, data=self.login_payload, verify=False)
                response = s_obj.get(self.download_url, stream=True, verify=False)
                target_path = self.job_path + '/Backup/' + currentndbzipfile
                handle = open(target_path, "wb")
                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        handle.write(chunk)
                handle.close()
            #server_link = ['ssh '+ str(self.server_ip)]
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.server_ip, port=22, username=self.server_username, password=self.server_pwd)
            logger.info("Stopping the current NDB")
            cmd1 = 'cd '+ self.server_oldpath
            cmd2 = './runxnc.sh -stop'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            self.old_ndbversion = ndb_version
            while not stdout.channel.eof_received:
                out = stdout.read()
                if "Stopped!" in out:
                    logger.info("Current NDB %s is stopped as expected", ndb_version)
                else:
                    logger.error(out)
                    logger.error("Current NDB %s could not be stopped. Pls check",
                                 ndb_version)
            time.sleep(10)
            logger.info("Starting NDB %s", self.new_ndbversion)
            cmd1 = 'cd '+ self.server_newpath
            cmd2 = './runxnc.sh'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            while not stdout.channel.eof_received:
                out = stdout.readline()
                if "Minimum Required Disk Space" in out:
                    logger.error("Pls free up the space in NDB server and retry")
                    break
                if "Please upgrade current Java and restart Nexus Data Broker" in out:
                    logger.error("Please check JAVA_HOME variable,upgrade current java "
                                 "and restart NDB")
                    break
                if "NDB GUI can be accessed using below URL" in out:
                    logger.info("NDB %s started successfully", self.new_ndbversion)
                    startstatus = 1
                    break
            if startstatus != 1:
                logger.error("NDB %s not started", self.new_ndbversion)
                upgradeflag = 0
                return upgradeflag
            for _ in xrange(10):
                try:
                    with requests.session() as s_obj:
                        s_obj.get(self.web_url, verify=False)
                        login_response = s_obj.post(
                            self.login_url, data=self.login_payload, verify=False)
                        if login_response.status_code == 200:
                            break
                        else:
                            upgradeflag = 0
                            time.sleep(20)
                except Exception as content:
                    time.sleep(20)
            with requests.session() as s_obj:
                s_obj.get(self.web_url, verify=False)
                s_obj.post(self.login_url, data=self.login_payload, verify=False)
                zip_file = self.job_path + '/Backup/' + currentndbzipfile
                response = s_obj.post(
                    self.upload_url,
                    files={"archive": (zip_file, open(zip_file, 'rb'))},
                    verify=False)
                if response.status_code == 200:
                    logger.info("Zip file uploaded in NDB %s", self.new_ndbversion)
                else:
                    logger.error("Zip file not uploaded in NDB %s", self.new_ndbversion)
                    upgradeflag = 0
            logger.info("Restarting the NDB after uploading config")
            cmd1 = 'cd '+ self.server_newpath
            cmd2 = './runxnc.sh -stop'
            cmd3 = cmd1 + ' \n ' + cmd2
            ssh.exec_command(cmd3)
            time.sleep(10)
            cmd1 = 'cd '+ self.server_newpath
            cmd2 = './runxnc.sh'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            while not stdout.channel.eof_received:
                out = stdout.readline()
                if "Please upgrade current Java and restart Nexus Data Broker" in out:
                    logger.error("Please check JAVA_HOME variable,upgrade current java "
                                 "and restart NDB")
                    break
                if "NDB GUI can be accessed using below URL" in stdout.readline():
                    logger.info("NDB %s started successfully", self.new_ndbversion)
                    startstatus = 1
                    break
            if startstatus != 1:
                logger.error("NDB %s not started", self.new_ndbversion)
                upgradeflag = 0
                return upgradeflag
            logger.info("Waiting for configurations to come up post upgrade")
            for _ in xrange(15):
                try:
                    with requests.session() as s_obj:
                        s_obj.get(self.web_url, verify=False)
                        s_obj.post(self.login_url, data=self.login_payload, verify=False)
                        self.get_devices_url = (self.conn_type + "://" + self.server_ip + ":"
                                                +self.port+self.variable['get_device_url'])
                        get_devices_response = s_obj.get(self.get_devices_url, verify=False)
                        if (get_devices_response.status_code == 200
                                and len(get_devices_response.json()['nodeData'])
                                == self.num_of_devices):
                            upgradeflag = 1
                            break
                        else:
                            time.sleep(20)
                except Exception as content:
                    time.sleep(20)
            return upgradeflag
        except Exception as content:
            logger.error("%s", content)

    def clean_ndb_config(self, servernewpath):
        """Removing NDB configs through startup config files"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.server_ip, port=22, username=self.server_username, password=self.server_pwd)
            startstatus = 0
            upgradeflag = 1
            ndb_path = servernewpath
            # Stop NDB
            logger.info("Stopping NDB")
            cmd1 = 'cd '+ ndb_path
            cmd2 = './runxnc.sh -stop'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            while not stdout.channel.eof_received:
                out = stdout.read()
                if "Stopped!" in out:
                    logger.info("Current NDB is stopped as expected")
                else:
                    logger.error("Current NDB could not be stopped. Pls check")
            time.sleep(30)
            logger.info("Clean the NDB by removing config files")
            cmd1 = ('cd '+ ndb_path + '/configuration/startup/\nrm -rf '
                    + (' ').join(self.config_dict['startup']))
            cmd2 = ('cd '+ ndb_path + '/configuration/startup/default\nrm -rf  '
                    + (' ').join(self.config_dict['default']))
            cmd3 = cmd1 + '\n' + cmd2
            ssh.exec_command(cmd3)
            time.sleep(10)
            logger.info("Starting NDB")
            cmd1 = 'cd '+ ndb_path
            cmd2 = './runxnc.sh'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            while not stdout.channel.eof_received:
                out = stdout.readline()
                if "Please upgrade current Java and restart Nexus Data Broker" in out:
                    logger.error("Please check JAVA_HOME variable,upgrade current java "
                                 "and restart NDB")
                    break
                if "NDB GUI can be accessed using below URL" in out:
                    logger.info("NDB %s started successfully", self.new_ndbversion)
                    startstatus = 1
                    break
            if startstatus != 1:
                logger.error("NDB %s not started", self.new_ndbversion)
                upgradeflag = 0
            for _ in xrange(10):
                try:
                    with requests.session() as s_obj:
                        s_obj.get(self.web_url, verify=False)
                        login_response = s_obj.post(
                            self.login_url, data=self.login_payload, verify=False)
                        if login_response.status_code == 200:
                            upgradeflag = 1
                            break
                        else:
                            upgradeflag = 0
                            time.sleep(20)
                except Exception as content:
                    upgradeflag = 0
                    time.sleep(20)
            return upgradeflag
        except Exception as content:
            logger.error("%s", content)

    def get_ndb_data(self, ndb_version):
        """Get configuration details from NDB"""
        try:
            with requests.session() as s_obj:
                s_obj.get(self.web_url, verify=False)
                s_obj.post(self.login_url, data=self.login_payload, verify=False)
                ndb_data = {}
                ndb_data[ndb_version] = {}
                ndb_data[ndb_version]['devices'] = s_obj.get(
                    self.get_devices_url, verify=False)
                ndb_data[ndb_version]['ports'] = s_obj.get(
                    self.get_ports_url, verify=False)
                ndb_data[ndb_version]['filters'] = s_obj.get(
                    self.get_filters_url, verify=False)
                ndb_data[ndb_version]['connections'] = s_obj.get(
                    self.get_connections_url, verify=False)
                ndb_data[ndb_version]['devices_list'] = []
                ndb_data[ndb_version]['connections_list'] = []
                ndb_data[ndb_version]['ports_list'] = {}
                num_of_devices = len(
                    ndb_data[ndb_version]['devices'].json()['nodeData'])
                ndb_data[ndb_version]['filters_list'] = ndb_data[
                    ndb_version]['filters'].json().keys()
                for i in range(0, num_of_devices):
                    ndb_data[ndb_version]['devices_list'].append(
                        ndb_data[ndb_version]['devices'].json()[
                            'nodeData'][i]['nodeName'])
                for j in range(0, len(ndb_data[ndb_version]['connections'].json())):
                    ndb_data[ndb_version]['connections_list'].append(
                        ndb_data[ndb_version]['connections'].json()[j]['rule']['name'])
                for i in range(0, num_of_devices):
                    dev_id = ndb_data[ndb_version]['devices_list'][i]
                    ndb_data[ndb_version]['ports_list'][dev_id] = []
                for k in range(0, len(ndb_data[ndb_version]['ports'].json())):
                    node = ndb_data[ndb_version]['ports'].json()[k].keys()[0]
                    port = ndb_data[ndb_version]['ports'].json()[k][node]['name']
                    if 'Ethernet' not in ndb_data[ndb_version]['ports'].json()[
                            k][node]['name']:
                        port = port.replace('Eth', 'Ethernet')

                    ndb_data[ndb_version]['ports_list'][node].append(port)
                with open(self.reportfile, "a") as self.filepointer:
                    self.filepointer.write(
                        "\t\tDEVICES PRESENT IN NDB\n")
                    self.filepointer.write(
                        "\t\t**********************\n")
                    self.filepointer.write(
                        "\t\t"+ ', '.join(ndb_data[ndb_version]['devices_list']))
                    self.filepointer.write(
                        "\n\t\tFILTERS PRESENT IN NDB\n")
                    self.filepointer.write(
                        "\t\t************************\n")
                    self.filepointer.write(
                        "\t\t"+ ', '.join(ndb_data[ndb_version]['filters_list']))
                    self.filepointer.write(
                        "\n\t\tCONNECTIONS PRESENT IN NDB\n")
                    self.filepointer.write(
                        "\t\t****************************\n")
                    self.filepointer.write(
                        "\t\t"+ ', '.join(ndb_data[ndb_version]['connections_list']))
                for key in ndb_data[ndb_version]['ports_list'].keys():
                    with open(self.reportfile, "a") as self.filepointer:
                        self.filepointer.write(
                            "\n\t\tPORTS PRESENT IN NDB FOR DEVICE " + key + "\n")
                        self.filepointer.write(
                            "\t\t********************************************\n")
                        self.filepointer.write(
                            "\t\t"+ ', '.join(ndb_data[ndb_version]['ports_list'][key])
                            + '\n\n')
        except Exception as content:
            logger.error("%s", content)

    def ndb_import(self, jobpath, import_rerunflag):
        """Importing configurations to latest NDB"""
        try:
            import_flag = 1
            import_status = {}
            if import_rerunflag and "ndb_import" in self.migrate_state.keys():
                passed_devices = []
                for key in self.migrate_state['ndb_import'].keys():
                    if "ndb_import_status" in key:
                        continue
                    if self.migrate_state['ndb_import'][key]['import_status'] == "PASS":
                        passed_devices.append(key)
                import_json_file = jobpath + '/Backup/' + 'import.json'
                with open(import_json_file, 'r+') as fileobj:
                    import_rerun_data = json.load(fileobj)
                    import_rerun_datacopy = copy.deepcopy(import_rerun_data)
                fileobj.close()
                for dev in passed_devices:
                    for i in range(0, len(import_rerun_data['nodes'])):
                        if dev == import_rerun_data['nodes'][i]['ipAddress']:
                            del import_rerun_datacopy['nodes'][i]
                import_rerun_data = import_rerun_datacopy
                import_json_file = self.job_path + '/Backup/' + 'import.json'
                with open(import_json_file, 'w') as outfile:
                    json.dump(import_rerun_data, outfile)
                    outfile.close()
                self.migrate_state['ndb_import'] = OrderedDict()                                                                             
            else:
                logger.info("Editing the JSON file before import")
                export_json_file = jobpath + '/Backup/' + 'export.json'
                with open(export_json_file, 'r+') as fileobj:
                    export_data = json.load(fileobj)
                fileobj.close()
                icmpv6_support = self.mapping_dict['SUPPORT_ICMPV6']
                variants = icmpv6_support['variants']
                platform_tuple = tuple(icmpv6_support['startswith'])
                specific_platform = icmpv6_support['platforms']
                num_of_switches = len(export_data['nodes'])
                for i in range(0, num_of_switches):
                    export_data['nodes'][i]['connectionType'] = "NX"
                    export_data['nodes'][i]['nxPort'] = "80"
                    num_of_ports = len(export_data['nodes'][i]['portConfigurations'])
                    for j in range(0, num_of_ports):
                        if (export_data['nodes'][i]['portConfigurations'][j]['monitorPortType']
                                == 'Delivery'):
                            export_data['nodes'][i]['portConfigurations'][j]['blockRx'] = True
                        else:
                            export_data['nodes'][i]['portConfigurations'][j]['blockRx'] = True
                            export_data['nodes'][i]['portConfigurations'][j]['blockTx'] = True
                            icmp_flag = 0
                            platform_string = export_data['nodes'][i]['hardware'].split('-')[1]
                            platform = re.search(r'\d+\S+', platform_string).group()
                            particular_platform = any(substring in export_data['nodes'][i]['hardware']
                                                      for substring in specific_platform)
                            variant_check = any(substring in export_data['nodes'][i]['hardware']
                                                for substring in variants)
                            all_platform_check = platform.startswith(platform_tuple) and variant_check
                            if particular_platform or all_platform_check:
                                icmp_flag = 1
                            if icmp_flag == 1:
                                export_data['nodes'][i]['portConfigurations'][j][
                                    'dropICMPv6NSM'] = True
                import_json_file = jobpath + '/Backup/' + 'import.json'
                with open(import_json_file, 'w+') as fileobj1:
                    json.dump(export_data, fileobj1)
                fileobj1.close()
            logger.info("Importing the NDB configuration to NDB %s", self.new_ndbversion)
            with requests.session() as s_obj:
                s_obj.get(self.web_url, verify=False)
                s_obj.post(self.login_url, data=self.login_payload, verify=False)
                get_admin = s_obj.get(self.get_admin_url, verify=False)
                if get_admin.status_code != 200:
                    return 0
                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'application/json, text/javascript, */*; q=0.01'
                    }
                import_post_response = s_obj.post(
                    self.import_url,
                    files={"file": (import_json_file, open(import_json_file, 'rb'))},
                    verify=False)
                if import_post_response.status_code != 200:
                    import_flag = 0
                    self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                    return import_flag
                import_json_response = import_post_response.json()
                import_payload = import_json_response
                del import_payload['lastImported']
                import_payload['includeConnection'] = "true"
                import_payload['includeRedirection'] = "true"
                num_of_devices = len(import_json_response['nodes'])
                for i in range(0, num_of_devices):
                    import_payload['nodes'][i]['address'] = import_payload[
                        'nodes'][i]['ipAddress']
                    for key in self.devices_dict.keys():
                        if (import_payload['nodes'][i]['ipAddress']
                                == self.devices_dict[key]['host_name/IP']):
                            import_payload['nodes'][i]['userName'] = self.devices_dict[
                                key]['username']
                            import_payload['nodes'][i]['password'] = self.devices_dict[
                                key]['password']
                            import_payload['nodes'][i]['forceImport'] = "false"
                            import_payload['nodes'][i]['number'] = i+1
                import_apply_response = s_obj.post(
                    self.import_apply_url, data=json.dumps(import_payload),
                    headers=headers)
                self.migrate_state['ndb_import'] = OrderedDict()
                import_apply_flag = 0
                if import_rerunflag:
                    num_of_failed_devices = len(self.devices_dict) - len(passed_devices)
                    if (import_apply_response.status_code == 200
                            and len(import_apply_response.json()['capabilityList'])
                            == num_of_failed_devices):
                        logger.info("The devices are ready to be imported")
                        import_apply_flag = 1
                else:
                    if (import_apply_response.status_code == 200
                            and len(import_apply_response.json()['capabilityList'])
                            == num_of_devices):
                        logger.info("The devices are ready to be imported")
                        import_apply_flag = 1
                if not import_apply_flag:                     
                    logger.error("Few devices are not reachable from NDB")
                    for key in self.devices_dict.keys():
                        ipAdd = self.devices_dict[key]['host_name/IP']
                        import_status[ipAdd] = "FAIL"
                        if len(import_apply_response.json()['capabilityList']) == 0:
                            logger.error("None of devices are up and ready to be imported")
                            self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                            import_flag = 0
                            return import_flag
                        for i in range(0, len(import_apply_response.json()['capabilityList'])):
                            if (self.devices_dict[key][
                                    'host_name/IP'] == import_apply_response.json()[
                                        'capabilityList'][i]['ipAddress']):
                                import_status[ipAdd] = "PASS"
                        if import_status[ipAdd] != "PASS":
                            self.migrate_state['ndb_import'][ipAdd] = {}
                            self.migrate_state['ndb_import'][ipAdd]['import_status'] = "FAIL"
                            logger.error("Import not successful for device %s" % ipAdd)
                    import_flag = 0
                if (import_apply_response.status_code != 200
                        or len(import_apply_response.json()['capabilityList']) == 0):
                    logger.error("NDB import of data failed")
                    import_flag = 0
                    self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                    return import_flag
                import_continue_payload = import_apply_response.json()
                for i in range(0, num_of_devices):
                    import_continue_payload['accepted'] = True
                import_continue_response = s_obj.post(
                    self.import_continue_url, data=json.dumps(import_continue_payload),
                    headers=headers)
                if import_continue_response.status_code != 200:
                    logger.error("NDB import of data failed")
                    import_flag = 0
                    self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                    return import_flag
                else:
                    for i in range(0, len(import_continue_response.json()['nodes'])):
                        if import_continue_response.json()['nodes'][i]['status'] == 'Success':
                            node_ip = import_continue_response.json()['nodes'][i]['ipAddress']
                            self.migrate_state['ndb_import'][node_ip] = OrderedDict()
                            self.migrate_state['ndb_import'][node_ip]['import_status'] = "PASS"
                            logger.info("Import successful for device %s" % node_ip)
                        elif import_continue_response.json()['nodes'][i]['status'] == 'Partial':
                            node_ip = import_continue_response.json()['nodes'][i]['ipAddress']
                            self.migrate_state['ndb_import'][node_ip] = OrderedDict()
                            self.migrate_state['ndb_import'][node_ip]['import_status'] = "PARTIAL"
                            logger.info("Import not successful for device %s" % node_ip)
                            import_flag = 0
                            self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                    if import_flag == 0:
                        self.migrate_state['ndb_import']['ndb_import_status'] = "FAIL"
                    else:
                        self.migrate_state['ndb_import']['ndb_import_status'] = "PASS"
            return import_flag

        except Exception as content:
            logger.error("%s", content)
    def ndb_export(self):
        """Exporting configuration from latest NDB"""
        try:
            export_flag = 1
            logger.info("Exporting the NDB configuration from NDB %s",
                        self.new_ndbversion)
            with requests.session() as s_obj:
                s_obj.get(self.web_url, verify=False)
                s_obj.post(self.login_url, data=self.login_payload, verify=False)
                for _ in xrange(10):
                    try:
                        export_get_response = s_obj.get(self.export_get_url, verify=False)
                        if export_get_response.status_code == 200:
                            break
                        else:
                            time.sleep(20)
                    except Exception as content:
                        time.sleep(20)
                if export_get_response.status_code != 200:
                    logger.error("Export data is not being fetched in NDB."
                                 "Hence cannot export NDB config")
                    export_flag = 0
                    return export_flag
                else:
                    export_payload = export_get_response.json()
                    export_payload['includeRedirection'] = True
                    export_payload['includeConnection'] = True
                    headers = {
                        'Content-type': 'application/json',
                        'Accept': 'application/json, text/javascript'
                        }
                    export_post_response = s_obj.post(
                        self.export_get_url, data=json.dumps(export_payload),
                        headers=headers, verify=False)
                    if export_post_response.status_code != 200:
                        logger.error("Export data is not being fetched in NDB."
                                     "Hence cannot export NDB config")
                        export_flag = 0
                        return export_flag
                    else:
                        download_exportjson_url = (self.export_get_url + '/'
                                                   + export_payload['tokenId'])
                        download_exportjsonresponse = s_obj.get(
                            download_exportjson_url, verify=False)
                        if download_exportjsonresponse.status_code != 200:
                            logger.error("Export data is not being fetched in NDB."
                                         "Hence cannot export NDB config")
                            export_flag = 0
                            return export_flag
                        num_of_devices = len(
                                download_exportjsonresponse.json()['nodes'])
                        logger.info("Checking if all the device configs got exported")
                        if num_of_devices != len(self.devices_dict):
                            logger.error("All the devices did not get exported")
                            logger.error("Pls check if all devices are up")
                            export_flag = 0
                            return export_flag
                        for i in range(0, num_of_devices):
                            if download_exportjsonresponse.json()['nodes'][i]['ipAddress'] == "":
                                for switch_key in self.devices_dict.keys():
                                    if download_exportjsonresponse.json()['nodes'][i]['nodeId'] in self.devices_dict[switch_key]['dpid']:
                                        download_exportjsonresponse.json()['nodes'][i]['ipAddress'] = self.devices_dict[switch_key]['host_name/IP']
                                    else:
                                        export_flag = 0
                                        logger.error("Failed on mapping DPID to IP address in %s", download_exportjsonresponse.json()['nodes'][i]['nodeId'])
                                        return export_flag
                        export_json_file = self.job_path + '/Backup/' + 'export.json'
                        with open(export_json_file, 'w') as outfile:
                            json.dump(download_exportjsonresponse.json(), outfile)
                        outfile.close()
            return export_flag
        except Exception as content:
            logger.error("%s", content)

    def ndb_revert(self):
        """Reverting older NDB configurations"""
        try:
            logger.info("Reverting back to %s NDB", self.old_ndbversion)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.server_ip, port=22, username=self.server_username,
                        password=self.server_pwd)
            # Stop the latest NDB if its running
            java_cmd = 'ps -ef | grep java'
            latest_ndb_flag = 0
            _, stdout, _ = ssh.exec_command(java_cmd)
            count = 0
            while not stdout.channel.eof_received:
                time.sleep(1)
                count = count + 1
                if stdout.channel.eof_received or count > 10:
                    break
            
            if self.server_newpath in stdout.readline():
                latest_ndb_flag = 1
            if latest_ndb_flag == 1:
                cmd1 = 'cd '+ self.server_newpath
                cmd2 = './runxnc.sh -stop'
                cmd3 = cmd1 + ' \n ' + cmd2
                _, stdout, _ = ssh.exec_command(cmd3)
                count = 0
                while not stdout.channel.eof_received:
                    time.sleep(1)
                    count = count + 1
                    if stdout.channel.eof_received or count > 10:
                        break
                if ("Controller with PID:" in stdout.readline()
                        and "Stopped" in stdout.readline()):
                    logger.info("NDB %s stopped successfully", self.new_ndbversion)
            cmd1 = 'cd '+ self.server_oldpath
            cmd2 = './runxnc.sh'
            cmd3 = cmd1 + ' \n ' + cmd2
            _, stdout, _ = ssh.exec_command(cmd3)
            count = 0
            while not stdout.channel.eof_received:
                time.sleep(1)
                count = count + 1
                if stdout.channel.eof_received or count > 10:
                    break
            out = stdout.readline()
            if "to connect to it please SSH to this host on port 2400" in out:
                logger.info("NDB %s started successfully", self.old_ndbversion)
                return 1
            elif "Another instance of controller running" in out:
                logger.info("Another instance of controller running")
                return 1
            else:
                logger.error("NDB %s not started", self.old_ndbversion)
                return 0
        except Exception as content:
            logger.error("%s", content)

def get_platform(conn):
    """Returns the platform of the switch"""
    try:
        cmd = 'sh ver | inc ignore-case Chassis'
        conn.execute(cmd)
        out = conn.response.strip(cmd)
        for line in out.split("\n"):
            line = line.strip()
            if ("Chassis" in line or 'chassis' in line) and 'cisco' in line:
                if len(line.split()) >= 4:
                    platform = line.split()[2]
                    platform_flag = 1
                else:
                    platform = line.split()[1]
                    platform_flag = 1
        if platform_flag == 1:
            platform = re.search(r'\d+\S+', platform).group()
            return platform
    except Exception as content:
        logger.error("Error while trying to get the platform of the switch")
        logger.debug(content)
def check_device_support(devices_dict, rerun_flag, backup_file):
    """Check for device support based on input file"""
    try:
        support_flag = 1
        backup_file = backup_file
        for dev_id in devices_dict.keys():
            switch_ip = devices_dict[dev_id]["host_name/IP"]
            username = devices_dict[dev_id]["username"]
            password = devices_dict[dev_id]["password"]
            tcam_regions = {}
            if 'tcam_regions' in devices_dict[dev_id].keys():
                tcam_regions = copy.deepcopy(devices_dict[dev_id]["tcam_regions"])
            account = Account(username, password)
            conn = SSH2()
            try:
                conn.connect(switch_ip)
                val = conn.login(account)
                if val != None:
                    logger.error("Authentication failure in %s", switch_ip)
                    support_flag = 0
                    break
            except:
                logger.error("Authentication failure in %s", switch_ip)
                support_flag = 0
                break
            conn.execute("terminal length 0")
            if rerun_flag == 0:
                # Get device image
                dev_image = Migrate.get_version(conn)
                dev_image = dev_image[0]
                # Check for device space issue
                conn.execute("copy running-config " + backup_file)
                if "No space left on device" in conn.response:
                    logger.error("Failed to create running-config as backup file in %s", switch_ip)
                    support_flag = 0
                    break
                conn.execute("show openflow switch 1")
                show_output = conn.response
                dpid_resp = dpid_parser(show_output)
                if dpid_resp:
                    devices_dict[dev_id]['dpid'] = dpid_resp
                else:
                    logger.error("Unable to fetch DPID value for %s", switch_ip)
                    support_flag = 0
                    break
            platform = get_platform(conn)
            if "3548" in platform:
                logger.error("%s platform not supported for migration in %s",
                             platform, switch_ip)
                support_flag = 0
                break
            # Check tcam values to be multiples of 256
            tcam_flag = 0
            for key, value in tcam_regions.iteritems():
                if int(value)%256 != 0:
                    logger.error("In Device %s, please provide the TCAM values"
                                 " in multiples of 256", switch_ip)
                    tcam_flag = 1
                    break
            if tcam_flag == 1:
                support_flag = 0
                break
            # Check for OVA present in device
            ofa_ova_name = ''
            if dev_image <= '7.0(3)I4(7)' and 'ofa_ova_name' not in devices_dict[dev_id].keys():
                logger.error("Openflow ova service name needs to be provided for switch %s in input file" % switch_ip)
                support_flag = 0
                break
            if dev_image > '7.0(3)I4(7)' and 'ofa_ova_name' in devices_dict[dev_id].keys():
                logger.error("Openflow ova service is not needed for switch %s with NXOS image %s" % (switch_ip, dev_image))
            if 'ofa_ova_name' in devices_dict[dev_id].keys():
                ofa_ova_name = copy.deepcopy(devices_dict[dev_id]["ofa_ova_name"])
                conn.execute("show virtual-service detail name "+ ofa_ova_name + " | json ")
                virtual_service_json = conn.response
                virtual_service_json = virtual_service_json.strip(
                    "show virtual-service detail name "+ ofa_ova_name + " | json ")
                virtual_service_json = virtual_service_json.strip()
                if len(virtual_service_json) == 0:
                    logger.error("Virtual service name '%s' not found in device %s",
                                 ofa_ova_name, switch_ip)
                    support_flag = 0
                    break
            # Check the bootflash content
            upgrades = [key for key, value in devices_dict[dev_id].iteritems()
                        if 'NXOS_Image' in key]
            if len(upgrades) > 0:
                conn.execute("dir bootflash: | no-more")
                for upgrade_item  in upgrades:
                    image = copy.deepcopy(devices_dict[dev_id][upgrade_item])
                    for key, value in image.iteritems():
                        if value not in conn.response:
                            logger.error("Nxos-Image %s not available in bootflash for %s",
                                         value, dev_id)
                            support_flag = 0
                            return support_flag
            conn.send("exit")
            conn.close()
        return support_flag

    except Exception as content:
        logger.error("Error while checking for device support")
        logger.debug(content)
        return 0

def dpid_parser(out):
    """Parse dpid from switch and convert its format"""
    try:
        formated_dpid = None
        dpid_out = out.split('\n')
        for line in dpid_out:
            if 'DPID' in line:
                line = line.strip()
                dpid = line.split(":")[1]
                temp = iter(dpid)
                formated_dpid = ':'.join(a+b for a,b in zip(temp,temp))
        return formated_dpid
    except Exception as content:
        logger.error("Error while checking for device support")
        logger.debug(content)
        
def get_runtime(devices_dict):
    """ Print the runtime of the script to user """
    try:
        num_of_devices = len(devices_dict.keys())
        num_of_singlenxosupgrade = 0
        num_of_twonxosupgrade = 0
        for key in devices_dict.keys():
            if "NXOS_Image1" in devices_dict[key].keys() and \
                "NXOS_Image2" in devices_dict[key].keys():
                num_of_twonxosupgrade = num_of_twonxosupgrade + 1
            if "NXOS_Image2" not in devices_dict[key].keys():
                num_of_singlenxosupgrade = num_of_singlenxosupgrade + 1
        time_dict_withtwonxosupgrade = {1:30, 2:35, 3:40, 4:45, 5:45, 6:50, 7:50, 8:55, 9:55, 10:60}
        time_dict_withoutupgrade = {1:20, 2:25, 3:30, 4:35, 5:35, 6:50, 7:50, 8:55, 9:55, 10:60}
        if num_of_devices > 10:
            num_of_iterations = num_of_devices / 10
            time_taken = time_dict_withoutupgrade[10]*num_of_iterations
            if num_of_twonxosupgrade != 0:
                time_taken_extra = 10 * num_of_twonxosupgrade
                total_time = time_taken + time_taken_extra
            else:
                total_time = time_taken
        else:
            time_taken = time_dict_withoutupgrade[num_of_devices]
            if num_of_twonxosupgrade != 0:
                time_taken_extra = 10 * num_of_twonxosupgrade
                total_time = time_taken + time_taken_extra
            else:
                total_time = time_taken
        print("The script run time would be %s minutes" % total_time)
        while True:
            input = raw_input("Do you want to continue [y/n]: ")
            if input == 'n':
                print("Stopping script run as per user input - %s"%input)
                sys.exit()
            elif input == 'y':
                break
            else:
                print('Please answer with "y" or "n"')
    except Exception as content:
        logger.error("Error while getting the script runtime")
        logger.debug(content)
        return 0

if __name__ == '__main__':
    try:
        input_file_path = None
        job_id = ''
        if len(sys.argv) == 5:
            if 'rerun' in sys.argv[1].lower():
                if sys.argv[3] == '-p' and sys.argv[4] != '' and 'job.'in sys.argv[2].lower():
                    input_file_path = sys.argv[4]
                    job_id = sys.argv[2]
            if 'rerun' in sys.argv[3].lower():
                if sys.argv[1] == '-p' and sys.argv[2] != '' and 'job.'in sys.argv[4].lower():
                    input_file_path = sys.argv[2]
                    job_id = sys.argv[4]
        elif len(sys.argv) == 3:
            if sys.argv[1] == '-p' and sys.argv[2] != '':
                input_file_path = sys.argv[2]
            elif 'job.'in sys.argv[2].lower() and 'rerun' in sys.argv[1].lower():
                job_id = sys.argv[2]
        else:
            pass
        migrate_obj = NDBMigration(input_file_path)
        logger = logging.getLogger("Migration")
        logger.setLevel(logging.DEBUG)
        con_log_handler = logging.StreamHandler()
        file_log_handler = logging.FileHandler(migrate_obj.logfile)
        file_log_handler.setLevel(logging.DEBUG)
        con_log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_log_handler.setFormatter(formatter)
        con_log_handler.setFormatter(formatter)
        logger.addHandler(file_log_handler)
        logger.addHandler(con_log_handler)
        migrate_obj.ndb_migrate(job_id)

    except Exception as content:
        print (content)
