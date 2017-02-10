######################
# Author : Siva      #
#  Date  : 24/01/2017#
######################

import json
import re
import sys
import time
import logging
import os
import inspect
from collections import OrderedDict
import pexpect
import yaml
import requests
import pdb


class NdbValidator:

    def __init__(self, device_ip, username,
                 password, primary_mode,
                 supported_features, config,
                 final_device_flag,
                 NDB_Validator_dict,
                 device_name,
                 all_input_devices,
                 auxilary_mode=None):

        self.device_ip = device_ip
        self.username = username
        self.password = password
        self.primary_mode = primary_mode
        self.auxilary_mode = auxilary_mode
        self.supported_features = supported_features
        self.config = config
        self.final_device_flag = final_device_flag
        self.NDB_Validator_dict = NDB_Validator_dict
        self.device_name = device_name
        self.all_input_devices = all_input_devices
        self.url = "http://" + self.device_ip + "/ins"
        self.hardware_config_feature_list = []

        if len(sys.argv) == 3:
            self.inputFileName = os.path.join(
                os.path.dirname(__file__), sys.argv[-1])
        self.featureConfigMap = os.path.join(os.path.dirname(
            __file__), 'Utilities/featureConfigMap.yaml')
        self.supportedFeaturesMap = os.path.join(os.path.dirname(
            __file__), 'Utilities/supportedFeaturesMap.yaml')
        os.system('rm -rf temp.log')
        os.system('rm -rf temp1.log')

        self.argsflag = 0
        try:
            if len(sys.argv) == 5:
                self.file1 = os.path.join(
                    os.path.dirname(__file__), sys.argv[2])
                self.argsflag = 1
        except:
            self.argsflag = 0

        if self.argsflag != 1:
            self.device_connect_status = 'FALSE'
            try:
                self.child = pexpect.spawn('telnet ' + self.device_ip)
                self.child.expect('login: ')
                self.child.sendline(self.username)
                self.child.expect('Password: ')
                self.child.sendline(self.password)
                self.child.expect("#")
            except:
                logger.error(
                    "Error while connecting to the device : " + self.device_ip)
                self.device_connect_status = 'FALSE'

            else:
                logger.info(
                    "Successflly logged into the device : " + self.device_ip)
                self.device_connect_status = 'TRUE'

        self.argflag = 0
        if len(sys.argv) == 5:
            self.file1 = sys.argv[2]
            self.argflag = 1
        else:
            self.child.logfile = open("temp.log", "w+")
            self.nf = open(os.devnull, 'w')
            sys.stdout = self.nf

        if self.argflag == 1:
            pass
        else:
            try:
                self.child.sendline("sh ver | inc ignore-case Chassis")
                self.child.sendline("sh ver | grep NXOS | grep version")
                self.child.sendline("sh ver | grep system | grep version")
                self.child.sendline("sh nxapi")
                self.child.sendline("sh run | inc pipeline")
                self.child.sendline("sh run int | inc trunk")
                self.child.sendline("sh int brief | inc up | exclude mgmt0")
                self.child.sendline("sh run | inc hard")
                self.child.sendline(
                    "sh run | inc hardware | inc tap-aggregation | inc l2drop")
                self.child.sendline(
                    "sh run | inc vlan | exc limit | exc config | exc switchport | exc spanning")
                self.child.sendline("sh run | inc spanning | exc enable")
                self.child.sendline("sh run int")
                self.child.expect([pexpect.EOF, pexpect.TIMEOUT])
                print (self.child.readline())
                self.child.logfile = sys.stdout
            except:
                logger.info(
                    "Error while getting current state of the device : " +
                    self.device_ip)

        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = "temp.log"

        self.myheaders = {'content-type': 'application/json'}
        self.sh_ver_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh ver",
                "output_format": "json"
            }
        }

        self.sh_run_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh run",
                "output_format": "json"
            }
        }

        self.nxapi_payload = {
            "ins__api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh nxapi",
                "output_format": "json"
            }
        }

        self.virtual_service_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh virtual-service list",
                "output_format": "json"
            }
        }

        self.sh_mgmt_int_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh int mgmt 0",
                "output_format": "json"
            }
        }
        self.sh_acl_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh access-list",
                "output_format": "json"
            }
        }
        self.sh_openflow_brief_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh openflow switch 1 flows brief",
                "output_format": "json"
            }
        }
        self.sh_module_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh module",
                "output_format": "json"
            }
        }
        self.sh_hardware_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh hardware",
                "output_format": "json"
            }
        }
        self.sys_uptime_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh system uptime",
                "output_format": "json"
            }
        }
        self.sh_int_payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": "sh int",
                "output_format": "json"
            }
        }

    def showVersion(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_ver_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showRun(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_run_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showModule(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_module_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showHardware(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_hardware_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showIntMgnt(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_mgmt_int_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showAccesslist(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_acl_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showVirtualServiceList(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.virtual_service_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showOpenFlowsBrief(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_openflow_brief_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showSystemUpTime(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sys_uptime_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def showInt(self):
        try:
            self.response = requests.post(
                self.url, data=json.dumps(
                    self.sh_int_payload), headers=self.myheaders, auth=(
                    self.username, self.password), verify=False).json()
            return self.response["ins_api"]["outputs"]["output"]["code"]
        except:
            return "400"

    def hw_nxos_with_cli(self):
        self.platform_flag = 0
        self.nxos_flag = 0
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if ("Chassis" in line or 'chassis' in line) and 'cisco' in line:
                    if len(line.split(" ")) >= 4:
                        self.platform = line.split(" ")[2]
                        self.platform_flag = 1
                    else:
                        self.platform = line.split(" ")[1]
                        self.platform_flag = 1

                elif 'grep' not in line and "system:" in line and "version" in line:
                    self.nxos = line.split(" ")[-1][:-1]
                    self.nxos_flag = 1
                elif "NXOS:" in line and "version" in line:
                    self.nxos = line.split(" ")[2]
                    self.nxos_flag = 1
                else:
                    pass

        if self.platform_flag == 1 and self.nxos_flag == 1:
            try:
                self.platform = int(re.search(r'\d+', self.platform).group())
                if len(sys.argv) == 3:
                    logger.info(
                        "Grepped platform and nxos version from the device : " +
                        self.device_ip)
                else:
                    logger.info(
                        "Grepped platform and nxos version from the device")
            except:
                if len(sys.argv) == 3:
                    logger.error(
                        "Error while grepping platform and \
                        nxos version from the device : " + self.device_ip)
                    return (0, 0, 0)
                else:
                    logger.error(
                        "Error while grepping platform and \
                        nxos version from the device")
                    return (0, 0, 0)
            return(self.platform, self.nxos, 1)
        else:
            return (0, 0, 0)

    def nxapi_with_cli(self):
        self.nxapi_flag = 1
        if self.nxapi_flag == 1:
            with open(self.dst) as f:
                for line in f:
                    line = line.strip()
                    if 'sh' not in line and "nxapi" in line:
                        if "disabled" in line or 'enabled' in line:
                            self.nxapi_status = line.split(" ")[-1]
                            self.nxapi_flag = 2

                    else:
                        pass

            if self.nxapi_flag == 2:
                if len(sys.argv) == 3:
                    logger.info(
                        "Grepped NXAPI feature status from the device : " +
                        self.device_ip)
                    return(self.nxapi_status, 1)
                else:
                    logger.info(
                        "Grepped NXAPI feature status from the device")
                    return(self.nxapi_status, 1)
            else:
                if len(sys.argv) == 3:
                    logger.error(
                        "Error while grepping NXAPI status from the device : " +
                        self.device_ip)
                    return("disabled", 0)
                else:
                    logger.error(
                        "Error while grepping NXAPI status from the device")
                    return("disabled", 0)

    def pipeline(self, platform):
        self.nxapi_flag = 0
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if "inc" not in line:
                    if "pipeline" in line:
                        if "201" in line:
                            logger.warn(
                                "3500 series for openflow you need to set pipeline 203 and not pipeline 201")
                            NDB_Validator_dict[self.device_name]['others'].append(
                                "3500 series for openflow you need to set pipeline 203 and not pipeline 201")
                        elif "203" in line:
                            logger.warn(
                                "3500 series for openflow pipeline 203 is there")
                        else:
                            pass

                else:
                    pass

        return 1

    def ipv4_ipv6_image(self, nxos, aux_flag):
        self.nxos = nxos
        self.aux_flag = aux_flag
        with open(self.supportedFeaturesMap, 'r') as f:
            self.f_config = yaml.load(f)

        if self.aux_flag == 1:
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_both"]
        if 'of' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_of"]
        if 'nxapi' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_nxapi"]
        for feature in self.temp_list:
            if 'IPV6' in feature:
                if 'I5' in self.nxos:
                    logger.info(
                        "Verified >= I5 nxos iamge is there when IPV6 Filter is present")
                else:
                    logger.warn("IPV6 Filter  supports from NXOS I5")
                    NDB_Validator_dict[self.device_name]['others'].append(
                        "IPV6 Filter  supports from NXOS I5")

    def mpls_lb_qinq(self, nxapi, aux_flag):
        self.nxapi_status = nxapi
        self.aux_flag = aux_flag
        with open(self.supportedFeaturesMap, 'r') as f:
            self.f_config = yaml.load(f)

        if self.aux_flag == 1:
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_both"]
        if 'of' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_of"]
        if 'nxapi' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_nxapi"]
        for feature in self.temp_list:
            if "MPLS" in feature or "Load Balancing" in feature or "QinQ" in feature:
                if "enabled" in self.nxapi_status:
                    logger.info(
                        "Identified that NXAPI is enabled when MPLS/QinQ/Symmetric Load Balancing is there")
                else:
                    logger.warn(
                        "MPLS/Symmetric Load Balancing/QinQ features support only NXAPI enabled")
                    NDB_Validator_dict[self.device_name]['others'].append(
                        "MPLS/Symmetric Load Balancing/QinQ features support only NXAPI enabled")

    def redirection(self, nxapi, of):
        self.nxapi_status = nxapi
        self.of_status = of

        with open(self.supportedFeaturesMap, 'r') as f:
            self.f_config = yaml.load(f)

        if self.aux_flag == 1:
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_both"]
        if 'of' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_of"]
        if 'nxapi' in self.primary_mode.lower():
            self.temp_list = self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                ["HARDWARE"][self.platform]["supported_features_nxapi"]
        for feature in self.temp_list:
            if "redirection" in feature:
                if "enabled" in self.nxapi_status and self.of_status == 'Activated':
                    logger.info(
                        "Identified that OF + NXAPI is there when redirection")
                else:
                    logger.warn(
                        "Redirection is Supported only when OF + NXAPI")
                    NDB_Validator_dict[self.device_name]['others'].append(
                        "Redirection is Supported only when OF + NXAPI")

    def trunk_port(self):
        self.nxapi_flag = 0
        trunk_flag = 0
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if "inc" not in line:
                    if "switchport" in line and "trunk" in line:
                        trunk_flag = 1
                else:
                    pass
        if trunk_flag == 1:
            if len(sys.argv) == 3:
                logger.info(
                    "Identified that switch-port trunk has configured in the device : " +
                    self.device_ip)
            else:
                logger.info(
                    "Identified that switch-port trunk has configured in the device")
        else:
            if len(sys.argv) == 3:
                logger.warn(
                    "switch-port trunk has to be configured in one of the interfaces in the device : " +
                    self.device_ip)
            else:
                logger.warn(
                    "switch-port trunk has to be configured in one of the interfaces in the devic")

            NDB_Validator_dict[self.device_name]['others'].append(
                "switch-port trunk has to be configured in one of the interfaces")
        return 1

    def intSpeed(self):
        PortSpeedList = []
        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = 'temp.log'
        with open(self.dst) as f:
            self.SpeedFlag = 0
            for line in f:
                line = line.strip()
                if "inc" not in line:
                    if "eth" in line and 'up' in line:
                        self.SpeedFlag += 1
                        line = line.strip()
                        self.no_empty_str_list = filter(None, line.split(" "))
                        self.speed = self.no_empty_str_list[-2]
                        try:
                            PortSpeedList.append(
                                int(re.search(r'\d+', self.speed).group()))
                        except:
                            pass
                else:
                    pass
        return PortSpeedList

    def bpduFilterCheck(self):
        self.upportList = []
        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = 'temp.log'
        with open(self.dst) as filePoint:
            for line in filePoint:
                if 'inc' not in line:
                    if "eth" in line and 'up' in line:
                        line = line.strip()
                        self.no_empty_str_list = filter(None, line.split(" "))
                        self.upportList.append(self.no_empty_str_list[0])

            for itemIndex in range(len(self.upportList)):
                self.upportList[itemIndex] = self.upportList[itemIndex][3:]
        with open(self.dst) as filePoint:
            self.totalCount = 0
            self.flag = 0
            for line in filePoint:
                line = line.strip()
                if 'interface Ethernet' in line:
                    self.flag = 0
                    for item in self.upportList:
			verifyitemlength = len(line.split(" ")[-1][8:])
                        if item in line and len(item) == verifyitemlength:
                            self.flag = 1

                if self.flag == 1:
                    if 'spanning-tree bpdufilter enable' in line:
                        self.totalCount += 1
                        self.flag = 0
        if len(self.upportList) == self.totalCount:
            return "true"
        else:
            return "false"

    def switchportCheck(self):
        self.upportList = []
        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = 'temp.log'
        with open(self.dst) as filePoint:
            for line in filePoint:
                if 'inc' not in line:
                    if "eth" in line and 'up' in line:
                        line = line.strip()
                        self.no_empty_str_list = filter(None, line.split(" "))
                        self.upportList.append(self.no_empty_str_list[0])

            for itemIndex in range(len(self.upportList)):
                self.upportList[itemIndex] = self.upportList[itemIndex][3:]

        with open(self.dst) as filePoint:
            self.totalCount = 0
            self.flag = 0
            for line in filePoint:
                line = line.strip()
                if 'interface Ethernet' in line:
                    self.flag = 0
                    for item in self.upportList:
			verifyitemlength = len(line.split(" ")[-1][8:])
                        if item in line and len(item) == verifyitemlength:
                            self.flag = 1
                if self.flag == 1:
                    if 'switchport mode trunk' in line:
                        self.totalCount += 1
                        self.flag = 0
        if len(self.upportList) == self.totalCount:
            return "true"
        else:
            return "false"

    def vlanRange(self):
        self.vlanList = []
        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = 'temp.log'
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if "inc" not in line and 'vlan' in line\
                        and 'no' not in line and 'switchport' not in line\
			and 'configuration' not in line:
                    line = line.strip()
                    self.vlanList = line[5:].split(",")
        return self.vlanList

    def mstCheck(self):
        self.mstflag = 0
        self.disvlan = []
        if self.argflag == 1:
            self.dst = sys.argv[2]
        else:
            self.dst = 'temp.log'
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if "inc" not in line and 'spanning-tree' in line\
                        and 'mst' in line:
                    self.mstflag = 1
                if 'inc' not in line and 'no' in line and \
                        'spanning-tree' in line:
                    line = line.replace("no spanning-tree vlan ", "")
                    self.disvlan = line.split(",")
        return self.mstflag, self.disvlan

    def mstCalCheck(self, vlanList, disvlanList):
        self.mstflag = 0
        self.vlanList = vlanList
        self.disvlanList = disvlanList
        self.dl = []
        for i in self.disvlanList:
            if len(i.split("-")) == 2:
                self.m = int(i.split("-")[0])
                self.n = int(i.split("-")[1])
                self.dl += (range(self.m, self.n + 1))
            else:
                self.dl.append(i)
        self.temp = 0
        self.dset = set(self.dl)
        for val in self.vlanList:
            if len(val.split("-")) == 2:
                self.m = int(val.split("-")[0])
                self.n = int(val.split("-")[1])
                if len(
                    self.dset.intersection(
                        range(
                            self.m,
                            self.n +
                            1))) == (
                    self.n -
                    self.m +
                        1):
                    self.temp += 1
            else:
		try:
                    if int(val) in self.dl:
                        self.temp += 1
		except:
		    pass
        if self.temp == len(self.vlanList):
            self.mstflag = 1
        return self.mstflag

    def L2Drop(self, mode, platform):
        self.nxapi_flag = 0
        drop_flag = 0
        self.NDB_Validator_dict[device]["problem"]['NXAPI'] = []
        with open(self.dst) as f:
            for line in f:
                line = line.strip()
                if "inc" not in line:
                    if "hardware" in line and "tap-aggregation" in line and "l2drop" in line:
                        drop_flag = 1
                else:
                    pass
        if drop_flag == 1:
            logger.info(
                "Identified that L2Drop has configured in the device : " +
                self.device_ip)
        else:
            logger.warn(
                "L2Drop has to be configured in the device : " +
                self.device_ip)
            self.NDB_Validator_dict[device][
                "problem"]['NXAPI'].append("l2drop")
        return 1

    def hardwareConfiguration(self):
        self.sh_run_response = requests.post(
            self.url, data=json.dumps(
                self.sh_run_payload), headers=self.myheaders, auth=(
                self.username, self.password), verify=False).json()
        self.hardware_configuration = self.sh_run_response['ins_api']['outputs'][
            'output']['body']['filter']['configure']['terminal']['hardware']
        return self.hardware_configuration

    def supportMode(
            self,
            primary_mode,
            platform_version,
            nxos_version,
            aux_mode=None):
        with open(self.supportedFeaturesMap, 'r') as f:
            self.config = yaml.load(f)
        self.nxos_version = nxos_version
        self.version = platform_version
        self.primary_mode = primary_mode
        self.aux_mode = aux_mode
        self.all_modes = self.config['HW_NXOS_SUPPORTED_FEATURES'][
            'HARDWARE'][self.platform].keys()
        self.dev_mode_list = []
        for f_mode in self.all_modes:
            self.dev_mode_list.append(f_mode.split("_")[2])

        if self.aux_mode is None:
            if "3048" in str(self.version) or "3064" in str(self.version):
                if "U6" in self.nxos_version:
                    logger.error(
                        "Device : " +
                        self.device_ip +
                        " supports only OF if in U6 version")
                    return 0
            else:
                pass
            if self.primary_mode.lower() in self.dev_mode_list:
                logger.info("Device : " + self.device_ip +
                            " supports the " + self.primary_mode + " mode")
            else:
                logger.error(
                    "Device : " +
                    self.device_ip +
                    " does not support the " +
                    self.primary_mode +
                    " mode")
                return 0
        else:
            if "3048" in str(self.version) or "3064" in str(self.version):
                if "U6" in self.nxos_version:
                    if 'OF' in self.primary_mode:
                        logger.info(
                            "Device : " +
                            self.device_ip +
                            " supports the " +
                            self.primary_mode +
                            " mode")
                    else:
                        logger.error(
                            "Device : " +
                            self.device_ip +
                            " supports only OF if in U6 version")
                        return 0
            else:
                pass
            if self.aux_mode.lower() in "of":
                logger.error("Device : " + self.device_ip +
                             " does not support the OF mode as auxilary")
                return 0
            if 'both' in self.dev_mode_list:
                logger.info("Device : " + self.device_ip +
                            " supports both NXAPI and OF modes")
            else:
                logger.error(
                    "Device : " +
                    self.device_ip +
                    " does not support the " +
                    self.primary_mode +
                    " mode")
                return 0
        return 1

    def nxapi(self):
        self.nx_response = requests.post(
            self.url, data=json.dumps(
                self.nxapi_payload), headers=self.myheaders, auth=(
                self.username, self.password), verify=False).json()

        self.nx_status = self.nx_response['ins_api']['outputs'][
            'output']['body']['operation_status']['o_status']
        return self.nx_status

    def openFlow(self):
        self.of_response = requests.post(
            self.url, data=json.dumps(
                self.virtual_service_payload), headers=self.myheaders, auth=(
                self.username, self.password), verify=False).json()
        self.of_status = self.of_response['ins_api']['outputs'][
            'output']['body']['TABLE_list']['ROW_list']['status']

        self.of_name = self.of_response['ins_api']['outputs'][
            'output']['body']['TABLE_list']['ROW_list']['name']
        return self.of_status, self.of_name

    def hardwareConfiguration_cli(
            self,
            feature_list,
            mode,
            aux,
            platform,
            nxos):
        self.feature_list = feature_list
        self.mode = mode
        self.platform = platform
        self.aux_flag = aux
        self.nxos = nxos
        with open(self.featureConfigMap, 'r') as f:
            self.hardware_config = yaml.load(f)
        if self.aux_flag == 1:
            for feature in self.feature_list:
                self.verify_cmd = []
                if '9' in str(self.platform)[0]:
                    self.verify_cmd.append("openflow_double-wide")
                    self.verify_cmd.append("ifacl")
                elif '92160' in str(self.platform) or '92304' in str(self.platform):
                    self.verify_cmd.append("openflow_double-wide")
                    self.verify_cmd.append("ifacl")
                elif '93180' in str(self.platform):
                    self.verify_cmd.append("openflow_double-wide")
                    self.verify_cmd.append("ifacl")

                elif '3' in str(self.platform)[0]:
                    self.verify_cmd.append("profile_openflow")
                    self.verify_cmd.append("ifacl")
                else:
                    pass
                self.hardware_config_feature_list.append(feature)

            if self.argflag != 1:
                self.child.logfile = open("temp1.log", 'w+')
                for command in self.verify_cmd:
                    if len(command.split("_")) == 2:
                        self.child.sendline(
                            "sh run | grep " +
                            command.split("_")[0] +
                            " | inc " +
                            command.split("_")[1])
                    else:
                        self.child.sendline("sh run | grep " + command)
                self.child.expect([pexpect.EOF, pexpect.TIMEOUT])
                print (self.child.readline())
                time.sleep(3)
                self.child.logfile = sys.stdout

            if self.argflag != 1:
                self.dst = "temp1.log"
            else:
                self.dst = sys.argv[2]
            self.feature_flag = 1
            if self.feature_flag == 1:
                if isinstance(self.verify_cmd, list):
                    pass
                else:
                    self.verify_cmd = [self.verify_cmd]

                self.AllCommandsFlag = 0
                for feature in self.feature_list:
                    NDB_Validator_dict[device]['Global'][feature] = []
                    NDB_Validator_dict[device]['AUX'][feature] = []
                    NDB_Validator_dict[device]['OF'][feature] = []
                    NDB_Validator_dict[device]["problem"][feature] = []
                    if 'IPV6' in feature:
                        if 'I5' in self.nxos:
                            pass
                        else:
                            if len(sys.argv) == 3:
                                logger.error(
                                    feature + " feature not supported in the device : " + self.device_ip)
                                continue
                            else:
                                logger.error(
                                    feature + " feature not supported in the device")
                                continue
                    if 'MST' in feature:
                        continue
                    if 'bpdu' in feature or 'switchport' in feature:
                        continue
                    for command in self.verify_cmd:
                        self.command_flag = 0
                        with open(self.dst) as f:
                            for line in f:
                                line = line.strip()
                                if len(command.split("_")) == 2:
                                    if command.split("_")[0] in line and command.split("_")[
                                            1] in line and 'hardware' in line:
                                        self.command_flag += 1
                                        self.AllCommandsFlag += 1
                                else:
                                    if command in line and 'hardware' in line:
                                        self.command_flag += 1
                                        self.AllCommandsFlag += 1
                        if self.command_flag == 0:
                            NDB_Validator_dict[device]['AUX'][
                                feature].append(command)
                            NDB_Validator_dict[device][
                                "solution"].append(command)
                            NDB_Validator_dict[device]['Global'][
                                feature].append(command)

                    NDB_Validator_dict[device]["solution"] = list(
                        set(NDB_Validator_dict[device]["solution"]))
                    NDB_Validator_dict[device]['Global'][feature] = list(
                        set(NDB_Validator_dict[device]['Global'][feature]))
                    if self.AllCommandsFlag == len(self.verify_cmd):
                        if len(sys.argv) == 3:
                            logger.info(
                                feature +
                                " feature supported in the device : " +
                                self.device_ip)
                        else:
                            logger.info(
                                feature + " feature supported in the device")
                    else:
                        if 'Up Port Capacity' in feature:
                            pass
                        elif 'VLAN' in feature and 'Strip' not in feature:
                            pass
                        elif 'MST' in feature:
                            pass
                        elif 'bpdu' in feature or 'switchport' in feature:
                            pass
                        else:
                            if len(sys.argv) == 3:
                                logger.error(
                                    feature + " feature not supported in the device : " + self.device_ip)
                            else:
                                logger.error(
                                    feature + " feature not supported in the device")
                return 1
            else:
                return 1

        elif 'NXAPI' in self.mode:
            for feature in self.feature_list:
                if '92160' in str(
                        self.platform) or '92304' in str(
                        self.platform):
                    self.verify_cmd = ["ing-ifacl"]

                elif '93180' in str(self.platform):
                    self.verify_cmd = ["ing-ifacl"]

                else:
                    try:
                        self.verify_cmd = self.hardware_config["HARDWARE_CONFIG"][
                            "FEATURE"][feature]["CONFIG"]['NXAPI']
                        self.hardware_config_feature_list.append(feature)
                    except:
                        continue

                if self.argflag != 1:
                    self.child.logfile = open("temp1.log", 'w+')
                    for command in self.verify_cmd:
                        try:
                            self.child.sendline("sh run | grep " + command)
                        except:
                            if len(sys.argv) == 3:
                                logger.error(
                                    "Error while grepping hardware configuration from the device : " +
                                    self.device_ip)
                                return 0
                            else:
                                logger.error(
                                    "Error while grepping hardware configuration")
                                return 0
                        else:
                            if len(sys.argv) == 3:
                                logger.info(
                                    "Triggering to grep " +
                                    feature +
                                    " hardware configuration from the device : " +
                                    self.device_ip)
                            else:
                                logger.info(
                                    "Triggering to grep " + feature + " hardware configuration")
                    self.child.expect([pexpect.EOF, pexpect.TIMEOUT])
                    print (self.child.readline())
                    time.sleep(3)
                    self.child.logfile = sys.stdout
            if self.argflag != 1:
                self.dst = "temp1.log"
            else:
                self.dst = sys.argv[2]
            self.feature_flag = 1
            if self.feature_flag == 1:
                self.AllCommandsFlag = 0
		self.ingifacl = 0
                for feature in self.feature_list:
                    NDB_Validator_dict[device]['Global'][feature] = []
                    NDB_Validator_dict[device]['AUX'][feature] = []
                    NDB_Validator_dict[device]['OF'][feature] = []
                    NDB_Validator_dict[device]["problem"][feature] = []
                    if 'MST' in feature:
                        continue
                    elif 'bpdu' in feature or 'switchport' in feature:
                        continue
                    if 'Aggregate' in feature and '92160' not in str(
                            self.platform) and '92304' not in str(
                            self.platform) and '93180' not in str(self.platform) :
                        if ('3172' in str(self.platform) and '3164' not in str(self.platform) and '7' in self.nxos[
                                0]) or ('3' in str(self.platform)[0] and '7' in self.nxos[0]):
                            pass
                        else:
                            continue
                    if '92160' in str(
                            self.platform) or '92304' in str(
                            self.platform):
                        self.verify_cmd = ["ing-ifacl"]
                        self.feature_flag = 1
			self.ingifacl = 1

                    elif '93180' in str(self.platform):
                        self.verify_cmd = ["ing-ifacl"]
                        self.feature_flag = 1
			self.ingifacl = 1
 
                    else:
                        try:
                            self.verify_cmd = self.hardware_config["HARDWARE_CONFIG"][
                                "FEATURE"][feature]["CONFIG"]['NXAPI']
                            self.feature_flag = 1
                            self.hardware_config_feature_list.append(feature)
                        except:
			    continue

                    if 'IPV6' in feature:
                        if 'I5' in self.nxos and '3164' in str(
                                self.platform) or '32' in str(
                                self.platform)[
                                :2] or '9' in str(
                                self.platform)[0] and '92160' not in str(
                                self.platform):
                            pass
                        else:
                            if len(sys.argv) == 3:
                                logger.error(
                                    feature + " feature not supported in the device : " + self.device_ip)
                                continue
                            else:
                                logger.error(
                                    feature + " feature not supported in the device")
                                continue

                    self.verify_cmd = list(set(self.verify_cmd))
                    for command in self.verify_cmd:
                        self.command_flag = 0
                        with open(self.dst) as f:
                            for line in f:
                                line = line.strip()
                                if 'tap-aggregation' in command:
                                    if command in line and 'hardware' in line and 'profile' in line:
                                        self.command_flag += 1
                                        self.AllCommandsFlag += 1
                                else:
                                    if command in line and 'hardware' in line:
                                        self.command_flag += 1
                                        self.AllCommandsFlag += 1
                        if self.command_flag == 0:
                            NDB_Validator_dict[device]["problem"][
                                feature].append(command)
                            NDB_Validator_dict[device][
                                "solution"].append(command)
                            NDB_Validator_dict[device]['Global'][
                                feature].append(command)
                    NDB_Validator_dict[device]["solution"] = list(
                        set(NDB_Validator_dict[device]["solution"]))
                    NDB_Validator_dict[device]['Global'][feature] = list(
                        set(NDB_Validator_dict[device]['Global'][feature]))
                    if self.AllCommandsFlag == len(self.verify_cmd):
                        if len(sys.argv) == 3:
                            logger.info(
                                feature +
                                " feature supported in the device : " +
                                self.device_ip)
                        else:
                            logger.info(
                                feature + " feature supported in the device")
                    else:
                        if 'Up Port Capacity' in feature:
                            pass
                        elif 'VLAN' in feature and 'Strip' not in feature:
                            pass
                        elif 'MST' in feature:
                            pass
                        elif 'bpdu' in feature or 'switchport' in feature:
                            pass
                        else:
                            pass
                return 1
            else:
                return 1
        else:
            for feature in self.feature_list:
                if '3164' in str(
                        self.platform) or '32' in str(
                        self.platform)[
                        :2] or '9' in str(
                        self.platform)[0]:
                    self.verify_cmd = [
                        "controller_ipv4", "openflow_double-wide"]
                else:
                    self.verify_cmd = ["controller_ipv4", "profile_openflow"]
                self.hardware_config_feature_list.append(feature)

            if self.argflag != 1:
                self.child.logfile = open("temp1.log", 'a')
                for command in self.verify_cmd:
                    try:
                        if 'controller' in command:
                            self.child.sendline('sh run | inc controller')
                        else:
                            self.child.sendline(
                                "sh run | grep " +
                                command.split("_")[0] +
                                " | inc " +
                                command.split("_")[1])
                    except:
                        if len(sys.argv) == 3:
                            logger.error(
                                "Error while grepping hardware configuration from the device : " +
                                self.device_ip)
                            return 0
                        else:
                            logger.error(
                                "Error while grepping hardware configuration from the device")
                            return 0
                    else:
                        if len(sys.argv) == 3:
                            logger.info(
                                "Triggering to grep hardware configuration from the device : " +
                                self.device_ip)
                        else:
                            logger.info(
                                "Triggering to grep hardware configuration from the device")

                self.child.expect([pexpect.EOF, pexpect.TIMEOUT])
                print (self.child.readline())
                time.sleep(3)
                self.child.logfile = sys.stdout
            if self.argflag != 1:
                self.dst = "temp1.log"
            else:
                self.dst = sys.argv[2]
            self.feature_flag = 1
            if self.feature_flag == 1:
                if isinstance(self.verify_cmd, list):
                    pass
                else:
                    self.verify_cmd = [self.verify_cmd]

                self.all_command_count = 0
                for feature in self.feature_list:
                    NDB_Validator_dict[device]['Global'][feature] = []
                    NDB_Validator_dict[device]['AUX'][feature] = []
                    NDB_Validator_dict[device]['OF'][feature] = []
                    NDB_Validator_dict[device]["problem"][feature] = []
                    if 'MST' in feature:
                        continue
                    if 'bpdu' in feature or 'switchport' in feature:
                        continue
                    if 'IPV6' in feature:
                        if 'I5' in self.nxos:
                            pass
                        else:
                            if len(sys.argv) == 3:
                                logger.error(
                                    feature + " feature not supported in the device : " + self.device_ip)
                                continue
                            else:
                                logger.error(
                                    feature + " feature not supported in the device")
                                continue
                    for command in self.verify_cmd:
                        self.command_flag = 0
                        if "controller" in command:
                            with open(self.dst) as f:
                                for line in f:
                                    line = line.strip()
                                    if "controller" in line and'ipv4' in line and 'vrf' in line:
                                        self.command_flag += 1
                                        self.all_command_count += 1
                            if self.command_flag == 0:
                                NDB_Validator_dict[device]['OF'][
                                    feature].append(command)
                                NDB_Validator_dict[device]['Global'][
                                    feature].append(command)
                                NDB_Validator_dict[device][
                                    "solution"].append(command.split("_")[0])
                        else:
                            with open(self.dst) as f:
                                for line in f:
                                    line = line.strip()
                                    if command.split("_")[0] in line and command.split("_")[
                                            1] in line and 'hardware' in line:
                                        self.command_flag += 1
                                        self.all_command_count += 1
                            if self.command_flag == 0:
                                NDB_Validator_dict[device]['OF'][
                                    feature].append(command)
                                NDB_Validator_dict[device][
                                    "solution"].append(command)
                                NDB_Validator_dict[device]['Global'][
                                    feature].append(command)
                    NDB_Validator_dict[device]["solution"] = list(
                        set(NDB_Validator_dict[device]["solution"]))
                    NDB_Validator_dict[device]['Global'][feature] = list(
                        set(NDB_Validator_dict[device]['Global'][feature]))
                    if self.all_command_count == 2:
                        if len(sys.argv) == 3:
                            logger.info(
                                feature +
                                " feature supported in the device : " +
                                self.device_ip)
                        else:
                            logger.info(
                                feature + " feature supported in the device")
                    else:
                        if 'Up Port Capacity' in feature:
                            pass
                        elif 'VLAN' in feature and 'Strip' not in feature:
                            pass
                        elif 'MST' in feature:
                            pass
                        elif 'bpdu' in feature or 'switchport' in feature:
                            pass
                        else:
                            if len(sys.argv) == 3:
                                logger.error(
                                    feature + " feature not supported in the device : " + self.device_ip)
                            else:
                                logger.error(
                                    feature + " feature not supported in the device")
                return 1
            else:
                return 1

    def ndbValidator(self, aux_flag):
        for loop_val in range(1):
            self.aux_flag = aux_flag
            if self.aux_flag == 1:
                self.validator_obj = NdbValidator(
                    self.device_ip,
                    self.username,
                    self.password,
                    self.primary_mode,
                    self.supported_features,
                    self.config,
                    self.final_device_flag,
                    self.NDB_Validator_dict,
                    self.device_name,
                    self.all_input_devices,
                    self.auxilary_mode)

            else:
                self.validator_obj = NdbValidator(
                    self.device_ip,
                    self.username,
                    self.password,
                    self.primary_mode,
                    self.supported_features,
                    self.config,
                    self.final_device_flag,
                    self.NDB_Validator_dict,
                    self.device_name,
                    self.all_input_devices)

            if self.argflag != 1:
                if self.device_connect_status == 'FALSE':
                    os.system('rm -rf temp.log')
                    os.system('rm -rf temp1.log')
                    break

            if len(sys.argv) == 3:
                with open(self.inputFileName, 'r') as f:
                    feature_config = yaml.load(f)

            # Grepping platform and NXOS from the device
            self.platform, self.nxos, self.status = self.validator_obj.hw_nxos_with_cli()
            if self.status == 0:
                os.system('rm -rf temp.log')
                os.system('rm -rf temp1.log')
                break
            NDB_Validator_dict[self.device_name]['nxos']['os'] = self.nxos
            NDB_Validator_dict[self.device_name][
                'platform']['version'] = self.platform

            # Validating NXOS version is greater than U6
            if 'A8' in self.nxos or 'U6' in self.nxos or 'I2' in self.nxos or 'I3' in self.nxos or 'I4' in self.nxos or 'I5' in self.nxos:
                logger.info("Verified NXOS version")
            else:
                logger.error(
                    "Device : " +
                    self.device_ip +
                    " Does not supposrt current version. Upgrade the NXOS version")
                os.system('rm -rf temp.log')
                os.system('rm -rf temp1.log')
                break

            if self.argflag != 1:
                # Varifying NXAPI is enable or not
                self.nxapi_status, self.status = self.validator_obj.nxapi_with_cli()
                if self.status == 0:
                    os.system('rm -rf temp.log')
                    os.system('rm -rf temp1.log')
                    break

            if self.argflag != 1:
                if "enabled" in self.nxapi_status:
                    if len(sys.argv) == 3:
                        logger.info(
                            "Identified NXAPI status, NXAPI is enabled in the device : " +
                            self.device_ip)
                    else:
                        logger.info(
                            "Identified NXAPI status, NXAPI is enabled in the device")

                else:
                    if len(sys.argv) == 3:
                        logger.warn(
                            "Identified NXAPI status, NXAPI is not enabled in the device : " +
                            self.device_ip)
                    else:
                        logger.warn(
                            "Identified NXAPI status, NXAPI is not enabled in the device")

            # Validating mode
            if self.aux_flag == 1:
                self.status = self.validator_obj.supportMode(
                    self.primary_mode, self.platform, self.nxos, self.auxilary_mode)
            else:
                self.status = self.validator_obj.supportMode(
                    self.primary_mode, self.platform, self.nxos)

            if self.status == 0:
                os.system('rm -rf temp.log')
                os.system('rm -rf temp1.log')
                break
            if self.aux_flag == 1:
                NDB_Validator_dict[self.device_name]['mode']['name'] = 'AUX'
            else:
                NDB_Validator_dict[self.device_name][
                    'mode']['name'] = self.primary_mode
            # Verify Pipeline
            if str(self.platform)[0] == '3' and str(self.platform)[1] == '5':
                self.status = self.validator_obj.pipeline(self.platform)
                if self.status == 0:
                    os.system('rm -rf temp.log')
                    os.system('rm -rf temp1.log')
                    break

            # Verify trunk port
            #self.status = self.validator_obj.trunk_port()
            # if self.status == 0:
            #    os.system('rm -rf temp.log')
            #    os.system('rm -rf temp1.log')
            #    break

            #mpls, loadbalance, qinq
            if self.argflag != 1:
                self.validator_obj.mpls_lb_qinq(
                    self.nxapi_status, self.aux_flag)

            # If NXAPI already enabled perform all operation throguht REST call
            # else perform throught CLI
            if self.argflag != 1:
                if "enabled" in self.nxapi_status:

                    logger.info(
                        "Triggering REST calls to sandbox to validate all the show commands in the device : " +
                        self.device_ip +
                        "\n")
                    self.sh_ver_res = self.validator_obj.showVersion()
                    if self.sh_ver_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show version")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show version")

                    self.sh_run_res = self.validator_obj.showRun()
                    if self.sh_run_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show run")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show run")

                    self.sh_mode_res = self.validator_obj.showModule()
                    if self.sh_mode_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show module")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show module")

                    self.sh_hard_res = self.validator_obj.showHardware()
                    if self.sh_hard_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show hardware")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show hardware")

                    self.sh_int_mgmt_res = self.validator_obj.showIntMgnt()
                    if self.sh_int_mgmt_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show int mgmt 0")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show int mgmt 0")

                    self.sh_acl_res = self.validator_obj.showAccesslist()
                    if self.sh_acl_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("show access-lists")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("show access-lists")

                    if 'OF' in self.primary_mode:
                        self.sh_virtual_ser_res = self.validator_obj.showVirtualServiceList()
                        if self.sh_virtual_ser_res == '200':
                            NDB_Validator_dict[self.device_name][
                                "yes_sh_comd"].append("show virtual-service list")
                        else:
                            NDB_Validator_dict[self.device_name][
                                "no_sh_cmd"].append("show virtual-service list")

                    self.sh_sysup_time_res = self.validator_obj.showSystemUpTime()
                    if self.sh_sysup_time_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("sh system uptime")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("sh system uptime")

                    self.sh_sysup_time_res = self.validator_obj.showInt()
                    if self.sh_sysup_time_res == '200':
                        NDB_Validator_dict[self.device_name][
                            "yes_sh_comd"].append("sh interface")
                    else:
                        NDB_Validator_dict[self.device_name][
                            "no_sh_cmd"].append("sh interface")

            with open(self.supportedFeaturesMap, 'r') as fp:
                self.f_config = yaml.load(fp)
            # Validating Supported Features
            if self.aux_flag == 1:
                self.static_feature_map = self.f_config["HW_NXOS_SUPPORTED_FEATURES"][
                    "HARDWARE"][self.platform]["supported_features_both"]
            if 'of' in self.primary_mode.lower():
                self.static_feature_map = self.f_config["HW_NXOS_SUPPORTED_FEATURES"][
                    "HARDWARE"][self.platform]["supported_features_of"]
            if 'nxapi' in self.primary_mode.lower():
                self.static_feature_map = self.f_config["HW_NXOS_SUPPORTED_FEATURES"][
                    "HARDWARE"][self.platform]["supported_features_nxapi"]

            self.port_capacity_list = self.validator_obj.intSpeed()
            self.port_capacity_list = list(set(self.port_capacity_list))
            if '3172' in str(
                    self.platform) and 'NXAPI' in self.primary_mode and '7' in self.nxos[0]:
                if 10 in self.port_capacity_list and 40 in self.port_capacity_list:
                    if 'I4(5)' in self.nxos or ('I4' in self.nxos and int(
                            self.nxos[-2]) > 5) or 'I5' in self.nxos:
                        self.status = self.validator_obj.L2Drop(
                            self.primary_mode, self.platform)
                        if self.status == 0:
                            os.system('rm -rf temp.log')
                            os.system('rm -rf temp1.log')
                            break
   		    else:
			pass
                else:
                    pass

            # Dynamic mapping
            # for feature in self.static_feature_map:
            self.status = self.validator_obj.hardwareConfiguration_cli(
                self.static_feature_map, self.primary_mode, self.aux_flag, self.platform, self.nxos)

            if len(sys.argv) == 3:
                with open(self.inputFileName, 'r') as f:
                    feature_config = yaml.load(f)

            if self.aux_flag == 1:
                self.NDB_Validator_dict[self.device_name]['features'] = \
                    self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                    ["HARDWARE"][self.platform]["supported_features_both"]
            if 'of' in self.primary_mode.lower():
                self.NDB_Validator_dict[self.device_name]['features'] = \
                    self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                    ["HARDWARE"][self.platform]["supported_features_of"]
            if 'nxapi' in self.primary_mode.lower():
                self.NDB_Validator_dict[self.device_name]['features'] = \
                    self.f_config["HW_NXOS_SUPPORTED_FEATURES"]\
                    ["HARDWARE"][self.platform]["supported_features_nxapi"]

            self.reference = os.path.join(os.path.dirname(
                __file__), 'Utilities/reference.yaml')
            with open(self.reference, 'r') as f:
                self.ref_config = yaml.load(f)
            if self.final_device_flag == 1:
                self.date_time = time.strftime("%c")
                if not os.path.isdir("Reports"):
                    os.makedirs("Reports")
                self.afile = os.path.join(os.path.dirname(
                    __file__), './Reports/NDBValidatorToolReport_' + str(self.date_time) + '.log')
                with open(self.afile, "a") as fp:
                    for device in self.all_input_devices:
                        fp.write("\n\n")
                        fp.write(
                            "\t\t*******************************************************\n")
                        if len(sys.argv) == 3:
                            fp.write(
                                "\t\tNDB VALIDATOR TOOL GENERATED REPORT FOR : " +
                                self.NDB_Validator_dict[device]['name'])
                        else:
                            fp.write(
                                "\t\tNDB VALIDATOR TOOL GENERATED REPORT FOR RUNNING CONFIG")

                        fp.write(
                            "\n\t\t*******************************************************\n\n")

                        if len(sys.argv) == 3:
                            fp.write(
                                "\nDEVICE                        :   " +
                                self.NDB_Validator_dict[device]['name'] +
                                "   " +
                                NDB_Validator_dict[device]['nxos']['os'] +
                                "   " +
                                NDB_Validator_dict[device]['mode']['name'])
                        else:
                            fp.write("\nDEVICE                        :   " + "   " +
                                     NDB_Validator_dict[device]['nxos']['os'] + "   " +
                                     sys.argv[-1])
                        if self.argflag != 1:
                            if "enabled" in self.nxapi_status:
                                if len(
                                        self.NDB_Validator_dict[device]['yes_sh_comd']) >= 1:
                                    fp.write(
                                        "\n\nWORKING NXAPI CLI             :   ")
                                for value in self.NDB_Validator_dict[
                                        device]['yes_sh_comd']:
                                    fp.write("\n")
                                    fp.write("\t\t\t\t  " + value)
                                if len(
                                        self.NDB_Validator_dict[device]['no_sh_cmd']) >= 1:
                                    fp.write(
                                        "\n\nNOT WORKING NXAPI CLI         :   ")
                                if len(
                                        self.NDB_Validator_dict[device]['no_sh_cmd']) >= 1:
                                    fp.write(
                                        "FOLLOWING NXAPI CLI NOT WORKING. PLEASE LOOK AT RECOMMENDATION\n")
                                else:
                                    fp.write(" - ")
                                for value in self.NDB_Validator_dict[
                                        device]['no_sh_cmd']:
                                    fp.write("\n")
                                    fp.write("\t\t\t\t  " + value)

                        with open(self.featureConfigMap, 'r') as f:
                            self.hardware_config = yaml.load(f)

                        self.hardware_feature_list = []
                        for feature in self.NDB_Validator_dict[
                                device]['features']:
                            try:
                                if self.hardware_config["HARDWARE_CONFIG"][
                                        "FEATURE"][feature]["CONFIG"][self.primary_mode]:
                                    self.hardware_feature_list.append(feature)
                            except:
                                pass

                        fp.write("\n\nPLATFORM SUPPORTED FEATURES   :   \n")
                        if len(sys.argv) == 3:
                            with open(self.inputFileName, 'r') as f:
                                self.input_config = yaml.load(f)

                        if len(sys.argv) == 3:
                            self.primary_mode = self.input_config[
                                'DEVICES'][device]['MODE']['primary']
                        else:
                            self.primary_mode = sys.argv[-1]

                        if len(sys.argv) == 3:
                            self.aux_flag = 0
                            try:
                                self.auxilary_mode = self.input_config[
                                    'DEVICES'][device]['MODE']['auxilary']
                                self.aux_flag = 1
                            except:
                                self.aux_flag = 0
                        else:
                            self.aux_flag = 0
                            if 'aux' in sys.argv[-1].lower():
                                self.aux_flag = 1

                        for value in self.NDB_Validator_dict[
                                device]['features']:
                            #fp.write("\n")
                            if self.aux_flag == 1:
                                if value in self.hardware_feature_list:
                                    fp.write("\n\n")
                                    if 'bpdu' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.bpduFilterCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append("bpdu")
                                        continue
                                    if 'switchport' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.switchportCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('switchport')
                                        continue
                                    if 'MST' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        self.mststatus, self.disvlanList = self.validator_obj.mstCheck()
                                        self.mstflag = self.validator_obj.mstCalCheck(
                                            self.vlanList, self.disvlanList)
                                        if self.mststatus == 1 and self.mstflag == 1:
                                            fp.write(" " + "Supports")
                                        elif self.mststatus == 1 and self.mstflag == 0:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst1')
                                        elif self.mststatus == 0 and self.mstflag == 1:
                                            fp.write(" " + "Do not supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst2')
                                        else:
                                            fp.write("Do not supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst3')
                                        continue
                                    if 'VLAN' in value and 'Strip' not in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        self.tem = 0
                                        for vlan in self.vlanList:
                                            fp.write(" " + str(vlan) + " ")
                                            self.tem += 1
                                        continue

                                    if 'Port Capacity' in value:
                                        fp.write("\t\t\t\t" + value + "  : ")
                                    else:
                                        fp.write("\t\t\t\t" + value + "  : ")
                                    self.port_capacity_list = self.validator_obj.intSpeed()
                                    self.port_capacity_list = list(
                                        set(self.port_capacity_list))
                                    for i in range(
                                            len(self.port_capacity_list)):
                                        if self.port_capacity_list[i] <= 40:
                                            self.port_capacity_list[i] = str(
                                                self.port_capacity_list[i]) + 'G'
                                    if 'Port Capacity' in value:
                                        if len(self.port_capacity_list) < 1:
                                            fp.write(" NO UP Interfaces")
                                            fp.write("\n")
                                        else:
                                            for pc in self.port_capacity_list:
                                                fp.write(
                                                    " " + str(pc) + "      ")
                                            fp.write("\n")
                                    else:
                                        if 'IPV6' in value:
                                            if 'I5' in NDB_Validator_dict[
                                                    device]['nxos']['os']:
                                                pass
                                            else:
                                                fp.write(
                                                    "Do not support. Please look at recomendations")
                                                NDB_Validator_dict[device][
                                                    'Global']['IPV6 Filter'] = []
                                                continue
                                        if len(
                                                self.NDB_Validator_dict[device]["AUX"][value]) >= 1:
                                            self.NDB_Validator_dict[device]["AUX"][value] = list(
                                                set(self.NDB_Validator_dict[device]["AUX"][value]))
                                            if len(
                                                    self.NDB_Validator_dict[device]["AUX"][value]) >= 1:
                                                fp.write(
                                                    "Do not support. Please look at recomendations")
                                        else:
                                            fp.write("Supports")
				    if 'MAC Address' in value:
					fp.write("\n") 
                                else:
                                    fp.write("\n")
                                    if 'bpdu' in value:
                                        fp.write("\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.bpduFilterCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('bpdu')
                                        continue
                                    if 'switchport' in value:
                                        fp.write("\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.switchportCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('switchport')
                                        continue

                                    if 'MST' in value:
                                        #fp.write("\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        self.mststatus, self.disvlanList = self.validator_obj.mstCheck()
                                        self.mstflag = self.validator_obj.mstCalCheck(
                                            self.vlanList, self.disvlanList)
                                        if self.mststatus == 1 and self.mstflag == 1:
                                            fp.write(" " + "Supports")
                                        elif self.mststatus == 1 and self.mstflag == 0:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst1')
                                        elif self.mststatus == 0 and self.mstflag == 1:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst2')
                                        else:
                                            fp.write("Do not supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst3')
                                        continue

                                    if 'VLAN' in value and 'Strip' not in value:
                                        fp.write("\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        for vlan in self.vlanList:
                                            fp.write(" " + str(vlan) + " ")
					fp.write("\n")
                                        continue
                                    if 'Port Capacity' in value:
                                        fp.write("\t\t\t\t" + value + "  : ")
                                    else:
                                        fp.write("\t\t\t\t" + value + "  : ")

                                    self.port_capacity_list = self.validator_obj.intSpeed()
                                    self.port_capacity_list = list(
                                        set(self.port_capacity_list))
                                    for i in range(
                                            len(self.port_capacity_list)):
                                        if self.port_capacity_list[i] <= 40:
                                            self.port_capacity_list[i] = str(
                                                self.port_capacity_list[i]) + 'G'
                                    if 'Port Capacity' in value:
                                        if len(self.port_capacity_list) < 1:
                                            fp.write(" NO UP Interfaces\n")
                                        else:
                                            for pc in self.port_capacity_list:
                                                fp.write(
                                                    " " + str(pc) + "       ")
                                    self.NDB_Validator_dict[device]["AUX"][value] = list(
                                        set(self.NDB_Validator_dict[device]["AUX"][value]))
                                    if 'IPV6' in value:
                                        if 'I5' in NDB_Validator_dict[
                                                device]['nxos']['os']:
                                            pass
                                        else:
                                            fp.write(
                                                "Do not support. Please look at recomendations")
                                            NDB_Validator_dict[device][
                                                'Global']['IPV6 Filter'] = []
                                            continue
                                    if len(self.NDB_Validator_dict[device]["AUX"][
                                           value]) >= 1 and 'Port Capacity' not in value:
                                        fp.write(
                                            "Do not support. Please look at recommendation\n")
                                    else:
                                        if 'Port Capacity' not in value:
                                            fp.write("Supports")
                            elif 'OF' in self.primary_mode:
                                if 'bpdu' in value:
                                    fp.write("\n\n")
                                    fp.write("\t\t\t\t" + value + "  : ")
                                    self.status = self.validator_obj.bpduFilterCheck()
                                    if 'true' in self.status:
                                        fp.write(" " + "Supports")
                                    else:
                                        fp.write(
                                            " " + "May or may not Supports")
                                        NDB_Validator_dict[device][
                                            'enhacements'].append('bpdu')
                                    continue
                                if 'switchport' in value:
                                    fp.write("\n\n")
                                    fp.write("\t\t\t\t" + value + "  : ")
                                    self.status = self.validator_obj.switchportCheck()
                                    if 'true' in self.status:
                                        fp.write(" " + "Supports")
                                    else:
                                        fp.write(
                                            " " + "May or may not Supports")
                                        NDB_Validator_dict[device][
                                            'enhacements'].append('switchport')
                                    continue

                                if 'MST' in value:
                                    fp.write("\n\n")
                                    fp.write("\t\t\t\t" + value + "  : ")
                                    self.vlanList = self.validator_obj.vlanRange()
                                    self.mststatus, self.disvlanList = self.validator_obj.mstCheck()
                                    self.mstflag = self.validator_obj.mstCalCheck(
                                        self.vlanList, self.disvlanList)
                                    if self.mststatus == 1 and self.mstflag == 1:
                                        fp.write(" " + "Supports")
                                    elif self.mststatus == 1 and self.mstflag == 0:
                                        fp.write(
                                            " " + "May or may not Supports")
                                        NDB_Validator_dict[device][
                                            'enhacements'].append('mst1')
                                    elif self.mststatus == 0 and self.mstflag == 1:
                                        fp.write(
                                            " " + "May or may not Supports")
                                        NDB_Validator_dict[device][
                                            'enhacements'].append('mst2')
                                    else:
                                        fp.write("Do not supports")
                                        NDB_Validator_dict[device][
                                            'enhacements'].append('mst3')
                                    continue

                                if 'VLAN' in value and 'Strip' not in value:
                                    fp.write("\n\n")
                                    fp.write("\t\t\t\t" + value + "  : ")
                                    self.vlanList = self.validator_obj.vlanRange()
                                    for vlan in self.vlanList:
                                        fp.write(" " + str(vlan) + " ")
                                    continue
                                if 'Port Capacity' in value:
                                    fp.write("\n\n\t\t\t\t" + value + "  : ")
                                else:
                                    fp.write("\n\n\t\t\t\t" + value + "  : ")

                                self.port_capacity_list = self.validator_obj.intSpeed()
                                self.port_capacity_list = list(
                                    set(self.port_capacity_list))
                                for i in range(len(self.port_capacity_list)):
                                    if self.port_capacity_list[i] <= 40:
                                        self.port_capacity_list[i] = str(
                                            self.port_capacity_list[i]) + 'G'

                                if 'Port Capacity' in value:
                                    if len(self.port_capacity_list) < 1:
                                        fp.write(" NO UP Interfaces")
                                    else:
                                        for pc in self.port_capacity_list:
                                            fp.write(" " + str(pc) + "     ")
                                else:
                                    if 'IPV6' in value:
                                        if 'I5' in NDB_Validator_dict[
                                                device]['nxos']['os']:
                                            pass
                                        else:
                                            fp.write(
                                                "Do not support. Please look at recomendations")
                                            NDB_Validator_dict[device][
                                                'Global']['IPV6 Filter'] = []
                                            continue
                                    if len(
                                            self.NDB_Validator_dict[device]["OF"][value]) >= 1:
                                        self.NDB_Validator_dict[device]["OF"][value] = list(
                                            set(self.NDB_Validator_dict[device]["OF"][value]))
                                        if len(
                                                self.NDB_Validator_dict[device]["OF"][value]):
                                            fp.write(
                                                " Do not support. Please look at recommendations")
                                        else:
                                            fp.write(" Supports")
                                    else:
                                        if 'Port Capacity' not in value:
                                            fp.write(" Supports")

                            else:
                                if value in self.hardware_feature_list:
                                    # fp.write("\n")
                                    if 'bpdu' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.bpduFilterCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('bpdu')
                                        continue
                                    if 'switchport' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.switchportCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('switchport')
                                        continue

                                    if 'MST' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        self.mststatus, self.disvlanList = self.validator_obj.mstCheck()
                                        self.mstflag = self.validator_obj.mstCalCheck(
                                            self.vlanList, self.disvlanList)
                                        if self.mststatus == 1 and self.mstflag == 1:
                                            fp.write(" " + "Supports")
                                        elif self.mststatus == 1 and self.mstflag == 0:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst1')
                                        elif self.mststatus == 0 and self.mstflag == 1:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst2')
                                        else:
                                            fp.write("Do not supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst3')
                                        continue

                                    if 'VLAN' in value and 'Strip' not in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        for vlan in self.vlanList:
                                            fp.write(" " + str(vlan) + " ")
                                        continue
                                    if 'Port Capacity' in value:
                                        fp.write("\n\n\t\t\t\t" +
                                                 value + "  : ")
                                    else:
                                        fp.write("\n\n\t\t\t\t" +
                                                 value + "  : ")

                                    self.NDB_Validator_dict[device]["problem"][value] = set(
                                        list(self.NDB_Validator_dict[device]["problem"][value]))
                                    if 'IPV6' in value:
                                        if 'I5' in NDB_Validator_dict[
                                                device]['nxos']['os']:
                                            pass
                                        else:
                                            fp.write(
                                                "Do not support. Please look at recomendations")
                                            NDB_Validator_dict[device][
                                                'Global']['IPV6 Filter'] = []
                                            continue
                                    if len(
                                            self.NDB_Validator_dict[device]["problem"][value]) >= 1:
                                        fp.write(
                                            " Do not support.Please look at recommendations")
                                    else:
                                        fp.write(" Supports")
                                else:
                                    if "Replicate" in value:
                                        try:
                                            if 'l2drop'in self.NDB_Validator_dict[
                                                    device]["problem"]['NXAPI']:
                                                fp.write(
                                                    "\n\n\t\t\t\t" + value + " : Do not support.Please look at recommendations")
                                                continue
                                        except:
                                            pass
                                    else:
                                        pass
                                    if 'bpdu' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.bpduFilterCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('bpdu')
                                        continue
                                    if 'switchport' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.status = self.validator_obj.switchportCheck()
                                        if 'true' in self.status:
                                            fp.write(" " + "Supports")
                                        else:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('switchport')
                                        continue

                                    if 'MST' in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        self.mststatus, self.disvlanList = self.validator_obj.mstCheck()
                                        self.mstflag = self.validator_obj.mstCalCheck(
                                            self.vlanList, self.disvlanList)
                                        if len(self.vlanList) == 0:
                                            fp.write(" " + "Do not Supports")
                                        elif self.mststatus == 1 and self.mstflag == 1:
                                            fp.write(" " + "Supports")

                                        elif self.mststatus == 1 and self.mstflag == 0:
                                            fp.write(
                                                " " + "May or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst1')
                                        elif self.mststatus == 0 and self.mstflag == 1:
                                            fp.write(
                                                " " + "may or may not Supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst2')
                                        else:
                                            fp.write("Do not supports")
                                            NDB_Validator_dict[device][
                                                'enhacements'].append('mst3')
                                        continue

                                    if 'VLAN' in value and 'Strip' not in value:
                                        fp.write("\n\n")
                                        fp.write("\t\t\t\t" + value + "  : ")
                                        self.vlanList = self.validator_obj.vlanRange()
                                        for vlan in self.vlanList:
                                            fp.write(" " + str(vlan) + " ")
                                        continue
                                    if 'Port Capacity' in value:
                                        fp.write("\n\n\t\t\t\t" +
                                                 value + "  : ")
                                    else:
                                        fp.write("\n\n\t\t\t\t" +
                                                 value + "  : ")

                                    self.port_capacity_list = self.validator_obj.intSpeed()
                                    self.port_capacity_list = list(
                                        set(self.port_capacity_list))
                                    for i in range(
                                            len(self.port_capacity_list)):
                                        if self.port_capacity_list[i] <= 40:
                                            self.port_capacity_list[i] = str(
                                                self.port_capacity_list[i]) + 'G'

                                    if 'Port Capacity' in value:
                                        if len(self.port_capacity_list) < 1:
                                            fp.write(" NO UP Interfaces")
                                        else:
                                            for pc in self.port_capacity_list:
                                                fp.write(
                                                    " " + str(pc) + "     ")
                                    else:
					if len(
                                            self.NDB_Validator_dict[device]["problem"][value]) >= 1\
					    and 'Port Capacity' not in value:
                                            fp.write(
                                                " Do not support.Please look at recommendations")
                                        else:
                                            fp.write(" Supports")

                                        #if 'Port Capacity' not in value:
                                        #    fp.write(" supports\n")
                        NDB_Validator_dict[self.device_name]['others'] = set(
                            list(NDB_Validator_dict[self.device_name]['others']))
                        if len(self.NDB_Validator_dict[device]['solution']) >= 1 or 'I5' not in\
                                NDB_Validator_dict[device]['nxos']['os'] or\
				len(NDB_Validator_dict[device]['enhacements']) >= 1:
                            fp.write(
                                "\n\nRECOMMENDATION                : CONFIGURE FOLLOWING MISSED CONFIGS\n")
                            for feature in NDB_Validator_dict[
                                    device]['Global'].keys():
				if 'MST' in feature or 'bpdu' in feature or 'switchport' in feature\
				    or 'IPV6' in feature or len(NDB_Validator_dict[device]['Global'][feature]) >= 1:
					fp.write("\n")
                                if "Port Capacity" in feature:
                                    continue
                                if 'VLAN' in feature and 'Strip' not in feature:
                                    continue
                                if 'MST' in feature:
                                    if 'mst2' in NDB_Validator_dict[
                                            device]['enhacements']:
                                        fp.write("\n")
                                        fp.write("\t\t\t\t" + feature +
                                                 "  : spanning-tree mode mst")
                                    elif 'mst1' in NDB_Validator_dict[device]['enhacements']:
                                        fp.write("\n")
                                        fp.write(
                                            "\t\t\t\t" + feature + "  : Spanning tree not disable on all vlans")
                                    elif 'mst3' in NDB_Validator_dict[device]['enhacements']:
                                        fp.write("\n")
                                        fp.write(
                                            "\t\t\t\t" +
                                            feature +
                                            "  : spanning-tree mode mst & Spanning tree disable on all vlans\n")
                                    else:
                                        pass
                                if 'bpdu' in feature:
                                    if 'bpdu' in NDB_Validator_dict[
                                            device]['enhacements']:
                                        fp.write("\n")
                                        fp.write(
                                            "\t\t\t\t" +
                                            feature +
                                            "  : spanning-tree bpdufilter should be there for ISL links")

                                if 'switchport' in feature:
                                    if 'switchport' in NDB_Validator_dict[
                                            device]['enhacements']:
                                        fp.write("\n")
                                        fp.write(
                                            "\t\t\t\t" +
                                            feature +
                                            "  : switchport mode trunk should be there for ISL links\n")
				
				if len(self.NDB_Validator_dict[device]['solution']) >= 1:
                                    #fp.write("\n")
				    pass

                                NDB_Validator_dict[device]['Global'][feature] = set(
                                    list(NDB_Validator_dict[device]['Global'][feature]))
                                if "Replicate" in feature:
                                    try:
                                        if 'l2drop' in self.NDB_Validator_dict[
                                                device]["problem"]['NXAPI']:
                                            fp.write(
                                                "\t\t\t\t" + feature + "  : hardware profile mode tap-aggregation l2drop\n")
                                    except:
                                        pass
                                else:
                                    pass

                                if 'IPV6' in feature:
                                    if 'I5' in NDB_Validator_dict[
                                            device]['nxos']['os']:
                                        if len(
                                                NDB_Validator_dict[device]['Global'][feature]) >= 1:
                                            fp.write("\n")
                                            fp.write("\t\t\t\t" +
                                                     feature + "  : ")
                                            value_list = NDB_Validator_dict[
                                                device]['Global'][feature]
                                        else:
                                            value_list = []
                                    else:
                                        fp.write(
                                            "\n\t\t\t\t" + feature + "  : IPV6 Filter supports from I5. Upgrade to I5")
                                        continue
                                else:
                                    if len(
                                            NDB_Validator_dict[device]['Global'][feature]) >= 1:
                                        fp.write("\n")
                                        fp.write("\t\t\t\t" + feature + "  : ")
                                        value_list = NDB_Validator_dict[
                                            device]['Global'][feature]
                                    else:
                                        value_list = []
                                if len(sys.argv) == 3:
                                    with open(self.inputFileName, 'r') as f:
                                        self.input_config = yaml.load(f)

                                for value in value_list:
                                    self.tempflag = 0
                                    if 'openflow_double-wide' in value or 'profile_openflow'\
                                            in value or 'controller' in value:
                                        self.platform = NDB_Validator_dict[
                                            device]['platform']['version']
                                        command = value
                                        if 'controller' in value:
                                            self.tempflag = 1
                                            #fp.write("\t\t\t\t"+value+"  : \n")
                                            fp.write(
                                                "\n\t\t\t\t\t\t" + "openflow\n")
                                            fp.write(
                                                "\t\t\t\t\t\t   " + "switch 1\n")
                                            fp.write(
                                                "\t\t\t\t\t\t      " + "pipeline 201/203\n")
                                            fp.write(
                                                "\t\t\t\t\t\t      " +
                                                "controller ipv4 <device/server ip> port <port number> vrf management security none\n")
                                            fp.write(
                                                "\t\t\t\t\t\t      " + "of-port interface <interfaces>\n")

                                        else:
                                            if len(value.split("_")) == 2:
                                                if 'AUX' in NDB_Validator_dict[
                                                        device]['mode']['name']:
                                                    if len(value_list) >= 2:
                                                        if "profile_openflow" in command and '3548' in str(
                                                                self.platform):
                                                            fp.write(
                                                                "\t\t\t\t\t\thardware profile forwarding-mode openflow-only")
                                                        else:
                                                            fp.write(
                                                                "\t\t\t\t\t\t " + self.ref_config['HW_CONFIG']['OF'][value])
                                                    else:
                                                        if "profile_openflow" in command and '3548' in str(
                                                                self.platform):
                                                            fp.write(
                                                                " hardware profile forwarding-mode openflow-only")
                                                        else:
                                                            fp.write(
                                                                " " + self.ref_config['HW_CONFIG']['OF'][value])
                                                else:
                                                    if "profile_openflow" in command and '3548' in str(
                                                            self.platform):
                                                        # fp.write(
                                                        #    " hardware profile forwarding-mode openflow-only")
                                                        fp.write(
                                                            "\t\t\t\t\t\thardware profile forwarding-mode openflow-only")
                                                    else:
                                                        # fp.write(
                                                        #        " " + self.ref_config['HW_CONFIG']['OF'][value])
                                                        fp.write("\n")
                                                        fp.write(
                                                            "\t\t\t\t\t\t " + self.ref_config['HW_CONFIG']['OF'][value])
                                                fp.write("\n")
                                            else:
                                                if 'AUX' in NDB_Validator_dict[
                                                        device]['mode']:
                                                    if len(value_list) >= 2:
                                                        if "profile_openflow" in command and '3548' in str(
                                                                self.platform):
                                                            fp.write(
                                                                "\t\t\t\t\t\thardware profile forwarding-mode openflow-only")
                                                        else:
                                                            fp.write(
                                                                "\t\t\t\t\t\t " + self.ref_config['HW_CONFIG']['OF'][value])
                                                    else:
                                                        if "profile_openflow" in command and '3548' in str(
                                                                self.platform):
                                                            fp.write(
                                                                " hardware profile forwarding-mode openflow-only")
                                                        else:
                                                            fp.write(
                                                                " " + self.ref_config['HW_CONFIG']['OF'][value])
                                                else:
                                                    if "profile_openflow" in command and '3548' in str(
                                                            self.platform):
                                                        fp.write(
                                                            " hardware profile forwarding-mode openflow-only")
                                                    else:
                                                        fp.write(
                                                            " " + self.ref_config['HW_CONFIG']['OF'][value])
                                                fp.write("\n")

                                    else:
                                        if 'AUX' in NDB_Validator_dict[
                                                device]['mode']['name']:
                                            if '3' in str(
                                                    NDB_Validator_dict[device]['platform']['version'])[0]:
                                                if len(value_list) >= 2:
                                                    fp.write(
                                                        "  " + "hardware profile tcam region ifacl <256/512/1024> double-wide")
                                                    fp.write("\n")
                                                else:
                                                    fp.write(
                                                        "  " + "hardware profile tcam region ifacl <256/512/1024> double-wide")
                                            else:
                                                if len(value_list) >= 2:
                                                    fp.write(
                                                        "  " + "hardware access-list tcam region ifacl <256/512/1024> double-wide")
                                                    fp.write("\n")
                                                else:
                                                    fp.write(
                                                        "  " + "hardware access-list tcam region ifacl <256/512/1024> double-wide")

                                        else:
                                            if 'HTTP Filter' in feature:
                                                self.tem = str(
                                                    NDB_Validator_dict[device]['platform']['version'])[0]
                                                if '3164' not in self.tem and '32' not in self.tem[
                                                        :2] and '3' in self.tem:
                                                    fp.write(
                                                        "  " + "hardware profile tcam region ifacl <256/512/1024> double-wide")
                                                    break
                                                else:
                                                    fp.write(
                                                        "  " + "hardware access-list tcam region ifacl <256/512/1024> double-wide")
                                                    break
                                            else:
                                                self.tem = str(
                                                    NDB_Validator_dict[device]['platform']['version'])[0]
                                                if len(value_list) >= 2:
                                                    if 'IPV4 Filter' in feature and '3164' not in self.tem\
                                                       and '32' not in self.tem[:2] and '3' in self.tem:
                                                        fp.write("\n")
                                                        fp.write(
                                                            "\t\t\t\t\t\t" + self.ref_config['HW_CONFIG']['NXAPI']['double-wide2'])
                                                    elif 'IPV6 Filter' in feature and '3164' in self.tem\
                                                            or '32' in self.tem[:2] or '9' in self.tem and '92160' in self.tem:
                                                        fp.write("\n")
                                                        fp.write(
                                                            "\t\t\t\t\t\t" + self.ref_config['HW_CONFIG']['NXAPI']['ipv6-ifacl'])
                                                    else:
                                                        fp.write("\n")
                                                        fp.write(
                                                            "\t\t\t\t\t\t" + self.ref_config['HW_CONFIG']['NXAPI'][value])
                                                else:
                                                    if 'IPV4 Filter' in feature and '3164' not in self.tem\
                                                       and '32' not in self.tem[:2] and '3' in self.tem:
                                                        fp.write(
                                                            "  " + self.ref_config['HW_CONFIG']['NXAPI']['double-wide2'])
                                                    elif 'IPV6 Filter' in feature and '3164' in self.tem\
                                                            or '32' in self.tem[:2] or '9' in self.tem\
                                                            and '92160' in self.tem:
                                                        fp.write(
                                                            "  " + self.ref_config['HW_CONFIG']['NXAPI']['ipv6-ifacl'])
                                                    else:
                                                        fp.write(
                                                            "  " + self.ref_config['HW_CONFIG']['NXAPI'][value])

                            if len(
                                    self.NDB_Validator_dict[device]['no_sh_cmd']) >= 1:
                                fp.write(
                                    "\t\t\t\t" + "NOT WORKING NXAPI CLI : Device can not add to NDB\n")
                                fp.write("\t\t\t\t\t\t\t" +
                                         "Reload the device\n")
                                if 'I3' in NDB_Validator_dict[device]['nxos']['os'] or 'I4' in \
                                        NDB_Validator_dict[device]['nxos']['os'] or 'I5' in \
                                        NDB_Validator_dict[device]['nxos']['os']:
                                    pass
                                else:
                                    fp.write(
                                        "\t\t\t\t\t\t\t" + "Upgrade the nxos greater than or equals to I3\n")
                                fp.write("\n")

                            fp.write("\n")
                            for value in NDB_Validator_dict[
                                    self.device_name]['others']:
                                fp.write("\t\t\t\t" + value)
                                fp.write("\n")
                                if 'pipeline' in value:
                                    fp.write("\t\t\t\t\t : pipeline 203")
                                    fp.write("\n")

                            fp.write("\n\n")

                os.system('rm -rf temp.log')
                os.system('rm -rf temp1.log')


if __name__ == '__main__':
    if not os.path.isdir("Log"):
        os.makedirs("Log")
        NDBLogFile = os.path.join(os.path.dirname(
            __file__), './Log/NDBValidatorToolLog.log')
    else:
        NDBLogFile = os.path.join(os.path.dirname(
            __file__), './Log/NDBValidatorToolLog.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    con_log_handler = logging.StreamHandler()
    file_log_handler = logging.FileHandler(NDBLogFile)
    file_log_handler.setLevel(logging.DEBUG)
    con_log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_log_handler.setFormatter(formatter)
    con_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)
    logger.addHandler(con_log_handler)

    if len(sys.argv) == 3:
        if sys.argv[1] == '-p'\
                and sys.argv[2] != '':
            pass
        else:
            logger.info("Please run as like below format")
            logger.info("python NDBValidator1.0.py -p <input file path>")
            sys.exit(0)
        inputfilearg = sys.argv[-1]
        inputfilename = os.path.join(os.path.dirname(__file__), inputfilearg)
        if os.path.exists(inputfilename):
            pass
        else:
            logger.error("Please provide valid input file path")
            sys.exit(0)
    else:
        if sys.argv[1] == '-p'\
                and sys.argv[2] != ''\
            and sys.argv[3] == '-m'\
                and sys.argv[4] != '':
            pass
        else:
            logger.info("Please run as like below format")
            logger.info(
                "python NDBValidator1.0.py -p <input file path> -m <mode>")
            sys.exit(0)

        inputfilearg = sys.argv[2]
        inputfilename = os.path.join(os.path.dirname(__file__), inputfilearg)
        if os.path.exists(inputfilename):
            pass
        else:
            logger.error("Please provide valid input file path")
            sys.exit(0)

        if 'AUX' in sys.argv[-1]\
           or 'NXAPI' in sys.argv[-1]\
           or 'OF' in sys.argv[-1]:
            pass
        else:
            logger.error("Please provide valid mode : AUX/OF/NXAPI")
            sys.exit(0)
    if len(sys.argv) == 3:
        filearg = sys.argv[-1]
        filename = os.path.join(os.path.dirname(__file__), filearg)
        try:
            with open(filename, 'r') as f:
                config = yaml.load(f)
        except:
            logger.error("Please provide valid input file path")
            sys.exit(0)

        all_input_devices = sorted(config['DEVICES'].keys())
        all_input_devices.sort(key=lambda x: int(x.split('_')[1]))
        num_of_devices = len(all_input_devices)
        NDB_Validator_dict = {}
        NDB_Validator_dict = OrderedDict()
    else:
        all_input_devices = ['DEVICE_1']
        NDB_Validator_dict = {}
        NDB_Validator_dict = OrderedDict()
    for device in all_input_devices:
        NDB_Validator_dict[device] = {}
        if len(sys.argv) == 3:
            try:
                NDB_Validator_dict[device]["name"] = config[
                    'DEVICES'][device]['CONNECTION']['ip']
            except:
                logger.info("Please provide the device details properly")
                sys.exit(0)
        NDB_Validator_dict[device]["yes_sh_comd"] = []
        NDB_Validator_dict[device]["no_sh_cmd"] = []
        NDB_Validator_dict[device]["features"] = []
        NDB_Validator_dict[device]["problem"] = {}
        NDB_Validator_dict[device]["solution"] = []
        NDB_Validator_dict[device]['others'] = []
        NDB_Validator_dict[device]['OF'] = {}
        NDB_Validator_dict[device]['AUX'] = {}
        NDB_Validator_dict[device]['Global'] = {}
        NDB_Validator_dict[device]['Global'] = OrderedDict()
        NDB_Validator_dict[device]['nxos'] = {}
        NDB_Validator_dict[device]['mode'] = {}
        NDB_Validator_dict[device]['platform'] = {}
        NDB_Validator_dict[device]['enhacements'] = []
        if len(sys.argv) == 3:
            try:
                device_ip = config['DEVICES'][device]['CONNECTION']['ip']
                username = config['DEVICES'][device]['CONNECTION']['username']
                password = config['DEVICES'][device]['CONNECTION']['password']
                primary_mode = config['DEVICES'][device]['MODE']['primary']
            except:
                logger.info("Please provide the device details properly")
                sys.exit(0)
        else:
            device_ip = ''
            username = ''
            password = ''

        if len(sys.argv) == 3:
            aux_flag = 0
            try:
                auxilary_mode = config['DEVICES'][device]['MODE']['auxilary']
                aux_flag = 1
            except:
                aux_flag = 0
        else:
            aux_flag = 0
            if sys.argv[-1].lower() == 'aux':
                aux_flag = 1
                primary_mode = 'OF'
                auxilary_mode = sys.argv[-1]
            else:
                primary_mode = sys.argv[-1]

        if len(sys.argv) == 3:
            try:
                supported_features = config['DEVICES'][
                    device]['SUPPORTED_FEATURES']['features']
            except:
                logger.info("Please provide the device details properly")
                sys.exit(0)
        else:
            config = ""
            supported_features = 'ALL'

        final_device_flag = 0
        if len(sys.argv) == 3:
            if all_input_devices.index(device) == (len(all_input_devices) - 1):
                final_device_flag = 1
        else:
            final_device_flag = 1

        if aux_flag == 1:
            validator_obj = NdbValidator(device_ip, username, password,
                                         primary_mode,
                                         supported_features, config,
                                         final_device_flag,
                                         NDB_Validator_dict,
                                         device, all_input_devices,
                                         auxilary_mode)
            validator_obj.ndbValidator(aux_flag)
        else:
            validator_obj = NdbValidator(device_ip, username, password,
                                         primary_mode,
                                         supported_features, config,
                                         final_device_flag,
                                         NDB_Validator_dict,
                                         device, all_input_devices)
            validator_obj.ndbValidator(aux_flag)
