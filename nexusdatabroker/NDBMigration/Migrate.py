""" Converting devices from openflow to NXAPI"""
import threading
import re
import time
import json
import pdb
import copy
import logging
from Exscript import Account
from Exscript.protocols import SSH2
from collections import OrderedDict

module_logger = logging.getLogger("Migration.device")
module_logger.setLevel(logging.INFO)
fail_flag = False
upgrade_fail_flag = False
def get_version(conn, lock=None):
    """ Returns the device version"""
    global fail_flag
    nxos_flag = 1
    try:
        cmd = 'show version | inc NXOS | inc version'
        conn.execute(cmd)
        out = conn.response.strip()
        out = out.strip(cmd)
        if out == '':
            cmd = 'show version | inc kickstart | inc version'
            conn.execute(cmd)
            nxos_flag = 0
        list1 = conn.response.strip(cmd)
        list1 = list1.split()
        version = list1[2]
        return version, nxos_flag
    except Exception as err_data:
        if lock:
            lock.acquire()
            fail_flag = True
            lock.release()
        module_logger.error("%s - Error while trying to get nx-os version from switch",
                            threading.current_thread().name)
        module_logger.debug(err_data)

def get_current_image(dev_dict):
    """Get actual image from the switch"""
    try:
        conn = dev_dict['conn_obj']
        current_image = {}
        cmd = ''
        if dev_dict['nxos_flag'] == 1:
            cmd = 'show version | inc NXOS | inc file'
            conn.execute(cmd)
            list1 = conn.response.strip(cmd)
            list1 = list1.split('bootflash:///')
            nxos_image = list1[1]
            current_image['nxos'] = nxos_image.strip()
        else:
            cmd = 'show version | inc kickstart | inc file'
            cmd1 = 'show version | inc system | inc file'
            conn.execute(cmd)
            list1 = conn.response.strip(cmd)
            list1 = list1.split('bootflash:///')
            kickstart_image = list1[1]
            conn.execute(cmd1)
            list2 = conn.response.strip(cmd1)
            list2 = list2.split('bootflash:///')
            system_image = list2[1]
            current_image['kickstart'] = kickstart_image.strip()
            current_image['system'] = system_image.strip()
        return current_image

    except Exception as err_data:
        module_logger.error("%s - Error while fetching current image from switch",
                            threading.current_thread().name)
        module_logger.debug(err_data)

def get_platform(conn, lock):
    """ Returns the switch platform"""
    global fail_flag
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
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while trying to get the platform of the "
                            "switch", (threading.current_thread().name))
        module_logger.debug(err_data)

def check_openflow_conf(conn, lock):
    """ Returns true/false based on the openflow configs"""
    global fail_flag
    try:
        cmd = "show running-config | include openflow"
        conn.execute(cmd)
        openflow_conf = conn.response
        openflow_conf = openflow_conf.strip(cmd)
        conf_list = openflow_conf.split('\n')
        word = 'openflow'
        return any(word in x for x in conf_list)
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while checking for openflow configuration "
                            "from switch", threading.current_thread().name)
        module_logger.debug(err_data)

def remove_openflow_conf(conn, lock, version, migrate_state):
    """ Removes all openflow related configurations from the device"""
    global fail_flag
    try:
        cmd = 'config terminal ; no openflow ; exit'
        conn.execute(cmd)
        nxos_version = ''
        if 'I' in version:
            version_pattern = re.compile("I\\d+")
            nxos_version = version_pattern.findall(version)[0]
        version_flag = 0
        if nxos_version != '' and int(nxos_version[1:]) >= 5:
            version_flag = 1
        if version_flag == 0:
            pass
        elif version_flag == 1:
            # Remove feature openflow for device version greater than I5
            cmd = 'config terminal ; no feature openflow ; exit'
            conn.execute(cmd)
            time.sleep(60)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_openflow_config'] = "PASS"

    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while removing openflow configuration "
                            "from switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_openflow_config'] = "FAIL"
        module_logger.debug(err_data)

def intf_parser(out, lock):
    """ Returns a object with interface name and its associated configuration"""
    global fail_flag
    try:
        parser_dict = {}
        lines = out.replace('\\r', '')
        lines = lines.replace('\r', '')
        lines = lines.replace('\\n', '\n')
        lines = lines.split("\n\n")
        for line in lines:
            line = line.strip(" ")
            if re.search(r'(interface)\s+(.*)', line, re.IGNORECASE):
                value = re.search(r'(interface)\s+(.*)', line, re.IGNORECASE)
                intf_key = value.group(2)
                if 'Ethernet' in intf_key or 'port-channel' in intf_key:
                    parser_dict[intf_key] = line.split('\n')
                    del_str = 'interface '+intf_key
                    parser_dict[intf_key].remove(del_str)
        return parser_dict
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while parsing interface configuration "
                            "from switch", threading.current_thread().name)
        module_logger.debug(err_data)

def remove_interface_conf(conn, lock, migrate_state):
    """ Remove the interface configs"""
    global fail_flag
    try:
        conn.execute('show running-config interface | no-more')
        interfaces_config = repr(conn.response)
        interface_list = intf_parser(interfaces_config, lock)
        for interface in interface_list.keys():
            if len(interface_list[interface]) != 0:
                command = ''
                if 'Ethernet' in interface:
                    intf_str = 'interface ethernet '+interface[8:]
                if 'port-channel' in interface:
                    intf_str = 'interface port-channel '+interface[12:]
                command += ';' + intf_str
                openflow_conf = [
                    'mode openflow', 'no lldp transmit',
                    'spanning-tree bpdufilter enable'
                ]
                for content in interface_list[interface]:
                    content = content.strip()
                    if content in openflow_conf:
                        if content == 'no lldp transmit':
                            content_str = 'lldp transmit'
                            command += ' ; ' + content_str
                        else:
                            content_str = 'no '+ content
                            command += ' ; ' + content_str
                    else:
                        content_str = 'no '+ content
                        command += ' ; ' + content_str
                command = 'configure terminal ' + command
                conn.execute(command)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_interface_config'] = "PASS"
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while trying to remove interface configuration "
                            "from switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_interface_config'] = "FAIL"
        module_logger.debug(err_data)

def remove_virtualsevice(conn, lock, switch_ova):
    """ Removing the openflow virtual service ova"""
    global fail_flag
    try:
        vname = switch_ova
        # removing virtual service list
        conn.execute("show virtual-service detail name "+ vname + " | json ")
        virtual_service_json = conn.response
        virtual_service_json = virtual_service_json.strip(
            "show virtual-service detail name "+ vname + " | json ")
        vservice_output = json.loads(virtual_service_json)
        vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
        pkg_name = vservice_output['TABLE_detail']['ROW_detail']['package_name']
        if "Activated" in vservice_state:
            try:
                conn.execute("conf t ; virtual-service "+  vname +" ; no activate")
                count = 0
                while count < 12:
                    time.sleep(5)
                    conn.execute("show virtual-service detail name "+ vname + " | json ")
                    virtual_service_json = conn.response
                    virtual_service_json = virtual_service_json.strip(
                        "show virtual-service detail name "+ vname + " | json ")
                    vservice_output = json.loads(virtual_service_json)
                    vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
                    if "Deactivated" in vservice_state:
                        module_logger.info("%s - Virtual service %s was successfully de-activated",
                                           threading.current_thread().name, vname)
                        break
                    else:
                        count += 1
            except:
                pass
        # Unprovisioning virtual_service
        unprovisioning_flag = 0
        if "Deactivated" in vservice_state:
            try:
                conn.execute("configure terminal ;no virtual-service "+  vname)
                unprovisioning_flag = 1
            except:
                pass
        # Uninstalling virtual service
        if unprovisioning_flag == 1:
            conn.execute('virtual-service uninstall name '+ vname)
            module_logger.info("%s - Virtual service %s was successfully uninstalled",
                               threading.current_thread().name, vname)
        return pkg_name
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while removing openflow virtual-service "
                            "ova from switch", threading.current_thread().name)
        module_logger.debug(err_data)

def remove_openflow_hard(conn, lock, migrate_state):
    """ Removing openflow hardware configurations"""
    global fail_flag
    try:
        cmd = "show running-config | grep hardware"
        conn.execute(cmd)
        device_hard_list = conn.response.strip(cmd)
        device_hard_list = device_hard_list.split('\n')
        for line in device_hard_list:
            if 'openflow' in line:
                line = line.strip()
                cmd = 'configure terminal ; no ' + line
                conn.execute(cmd)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_hardware_config'] = "PASS"
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while removing openflow hardware configuration "
                            "from switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'remove_hardware_config'] = "FAIL"
        module_logger.debug(err_data)

def add_nxapi_hard(conn, lock, platform, dev_dict, map_dict, migrate_state):
    """ Get the tcam values and create hardware command list based on that"""
    global fail_flag
    try:
        device_tcam_list = copy.deepcopy(dev_dict['tcam_regions'])
        hard_cmd_list = []
        for tcam_item in device_tcam_list:
            if 'tcam_ifacl' in tcam_item or 'tcam_ifacl-doublewide' in tcam_item:
                doublewide_flag = 0
                if 'doublewide' in tcam_item:
                    doublewide_flag = 1
                map_tcam = 'tcam_ifacl'
                acl_tuple = tuple(map_dict['access-list'][map_tcam]['startswith'])
                profile_tuple = tuple(map_dict['profile'][map_tcam]['startswith'])
                acl_platform = []
                profile_platform = []
                if map_dict['access-list'][map_tcam]['platforms'] is None:
                    acl_platform = []
                else:
                    acl_platform = copy.deepcopy(map_dict['access-list'][map_tcam]['platforms'])
                if map_dict['profile'][map_tcam]['platforms'] is None:
                    profile_platform = []
                else:
                    profile_platform = copy.deepcopy(map_dict['profile'][map_tcam]['platforms'])
                if (platform.startswith(acl_tuple) or
                        any(substring in platform for substring in acl_platform)):
                    hard_string = 'hardware access-list tcam region '
                    hard_cmd = hard_string + 'ifacl '+ dev_dict['tcam_regions'][tcam_item]
                    if doublewide_flag:
                        hard_cmd += ' double-wide'
                    hard_cmd_list.append(hard_cmd)
                elif (platform.startswith(profile_tuple) or
                      any(substring in platform for substring in profile_platform)):
                    hard_string = 'hardware profile tcam region '
                    hard_cmd = hard_string + 'ifacl '+ dev_dict['tcam_regions'][tcam_item]
                    if doublewide_flag:
                        hard_cmd += ' double-wide'
                    hard_cmd_list.append(hard_cmd)
                    hard_cmd1 = 'hardware profile tap-aggregation'
                    hard_cmd_list.append(hard_cmd1)
            else:
                acl_tuple = tuple(map_dict['access-list'][tcam_item]['startswith'])
                acl_platform = []
                if map_dict['access-list'][tcam_item]['platforms'] is None:
                    acl_platform = []
                else:
                    acl_platform = copy.deepcopy(map_dict['access-list'][tcam_item]['platforms'])
                if (platform.startswith(acl_tuple) or
                        any(substring in platform for substring in acl_platform)):
                    hard_string = 'hardware access-list tcam region '
                    tcam_type = ''
                    if 'tcam_ing-ifacl' in tcam_item:
                        tcam_type = 'ing-ifacl '
                    elif 'tcam_ipv6-ifacl' in tcam_item:
                        tcam_type = 'ipv6-ifacl '
                    elif 'tcam_mac-ifacl' in tcam_item:
                        tcam_type = 'mac-ifacl '
                    hard_cmd = hard_string + tcam_type + dev_dict['tcam_regions'][tcam_item]
                    hard_cmd_list.append(hard_cmd)
        module_logger.info("%s - List of hardware commands %s", threading.current_thread().name,
                           hard_cmd_list)
        migrate_state['device_conversion'][threading.current_thread().name][
            'add_nxapi_hardwareconfig'] = "PASS"
        for cmd_item in hard_cmd_list:
            cmd = 'configure terminal ; ' + cmd_item
            conn.execute(cmd)
            if 'ERROR' in conn.response or 'TCAM region configuration exceeded' in conn.response:
                lock.acquire()
                fail_flag = True
                lock.release()
                migrate_state['device_conversion'][threading.current_thread().name][
                    'add_nxapi_hardwareconfig'] = "FAIL"
                module_logger.error("%s - Error while configuring TCAM with below command\n", threading.current_thread().name, cmd_item)
                module_logger.debug("%s - Error with following exception\n%s\nNeed to revert "
                                    "the configs", threading.current_thread().name, conn.response)
                break
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while adding nxapi hardware configuration "
                            "to switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'add_nxapi_hardwareconfig'] = "FAIL"
        module_logger.error(err_data)

def check_ova_status(conn, vname):
    """Check for the status of OVA"""
    try:
        vname = vname
        vservice_state = None
        # removing virtual service list
        conn.execute("show virtual-service detail name "+ vname + " | json ")
        virtual_service_json = conn.response
        virtual_service_json = virtual_service_json.strip(
            "show virtual-service detail name "+ vname + " | json ")
        if virtual_service_json.strip() != '':
            vservice_output = json.loads(virtual_service_json)
            if 'TABLE_detail' in vservice_output.keys():
                vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
        return vservice_state

    except Exception as err_data:
        module_logger.debug(err_data)
        return None

def install_ova(conn, vname, pkg_name, state):
    """ Install a ova package and veriy it as installed state"""
    try:
        vservice_state = ''
        if "Installed" != state:
            cmd = 'virtual-service install name ' + vname + ' package bootflash:'+pkg_name
            conn.execute(cmd)
            try:
                count = 0
                while count < 12:
                    time.sleep(5)
                    conn.execute("show virtual-service detail name "+ vname + " | json ")
                    virtual_service_json = conn.response
                    virtual_service_json = virtual_service_json.strip(
                        "show virtual-service detail name "+ vname + " | json ")
                    vservice_output = json.loads(virtual_service_json)
                    vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
                    if "Installed" in vservice_state:
                        module_logger.info("%s - Virtual service %s was successfully "
                                           "installed", threading.current_thread().name, vname)
                        break
                    else:
                        count += 1
                cmd = 'conf t ; virtual-service ' + vname + ' ; activate'
                conn.execute(cmd)
                count = 0
                while count < 12:
                    time.sleep(5)
                    conn.execute("show virtual-service detail name "+ vname + " | json ")
                    virtual_service_json = conn.response
                    virtual_service_json = virtual_service_json.strip(
                        "show virtual-service detail name "+ vname + " | json ")
                    vservice_output = json.loads(virtual_service_json)
                    vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
                    if "Activated" in vservice_state:
                        module_logger.info("%s - Virtual service %s was successfully "
                                           "activated", threading.current_thread().name, vname)
                        break
                    else:
                        count += 1
            except Exception as content:
                pass
        elif "Installed" == state:
            try:
                cmd = 'conf t ; virtual-service ' + vname + ' ; activate'
                conn.execute(cmd)
                if "ERROR: Activate already configured for virtual-service" in conn.response:
                    cmd = 'conf t ; virtual-service ' + vname + ' ; no activate'
                    conn.execute(cmd)
                    cmd = 'conf t ; virtual-service ' + vname + ' ; activate'
                    conn.execute(cmd)
                count = 0
                while count < 12:
                    time.sleep(5)
                    conn.execute("show virtual-service detail name "+ vname + " | json ")
                    virtual_service_json = conn.response
                    virtual_service_json = virtual_service_json.strip(
                        "show virtual-service detail name "+ vname + " | json ")
                    vservice_output = json.loads(virtual_service_json)
                    vservice_state = vservice_output['TABLE_detail']['ROW_detail']['state']
                    if "Activated" in vservice_state:
                        module_logger.info("%s - Virtual service %s was successfully "
                                           "activated", threading.current_thread().name, vname)
                        break
                    else:
                        count += 1
            except Exception as content:
                pass
        return True
    except Exception as err_data:
        module_logger.error("%s - Error while installing OVA", threading.current_thread().name)
        module_logger.debug(err_data)
        return False

def hardware_parser(hard_content):
    """Parsing show run | grep hard list"""
    try:
        hard_list = []
        hard_content = hard_content.strip()
        hard_content = hard_content.replace('\r', '')
        hard_list = hard_content.split('\n')
        return hard_list
    except Exception as err_data:
        module_logger.error("%s - Error while parsing hardware TCAM configs",
                            threading.current_thread().name)
        module_logger.debug(err_data)

def revert_configs(dev_dict, migrate_state, backup_file):
    """ Reverting configs on failure"""
    try:
        conn = ''
        switch_ova = ''
        pkg_name = ''
        migrate_state = migrate_state
        migrate_state['revert_device_conversion'] = OrderedDict()
        switch_ip = dev_dict["host_name/IP"]
        username = dev_dict["username"]
        password = dev_dict["password"]
        account = Account(username, password)
        conn = SSH2(timeout=300)
        conn.connect(switch_ip)
        val = conn.login(account, flush=True)
        if val is None:
            pass
        else:
            count = 60
            switch_flag = 0
            for _ in xrange(count):
                try:
                    conn.connect(switch_ip)
                    if conn.response is None:
                        val = conn.login(account, flush=True)
                        if val is None:
                            switch_flag = 1
                            break
                except:
                    time.sleep(5)
            if switch_flag == 0:
                module_logger.info("%s - Unable to connect to device", threading.current_thread().name)
                module_logger.debug(err_data)
                migrate_state['revert_device_conversion'][threading.current_thread().name] = OrderedDict()
                migrate_state['revert_device_conversion'][threading.current_thread().name][
                    'overall_status'] = "FAIL"
                return dev_dict, migrate_state
        conn.execute('term len 0')
        conn.execute('term width 0')
        version, nxos_flag = get_version(conn)
        dev_dict['nxos_flag'] = nxos_flag
        dev_dict['conn_obj'] = conn
        if 'ofa_ova_name' in dev_dict.keys():
            switch_ova = copy.deepcopy(dev_dict['ofa_ova_name'])
        if 'pkg_name' in dev_dict.keys():
            pkg_name = copy.deepcopy(dev_dict['pkg_name'])
        if switch_ova != "":
            ova_state = check_ova_status(conn, switch_ova)
            if ova_state == "Not Installed" or not ova_state:
                install_response = install_ova(conn, switch_ova, pkg_name, ova_state)
                migrate_state['revert_device_conversion'][threading.current_thread().name] = OrderedDict()
                if install_response:
                    migrate_state['revert_device_conversion'][threading.current_thread().name][
                        'install_ova'] = "PASS"
                else:
                    migrate_state['revert_device_conversion'][threading.current_thread().name][
                        'install_ova'] = "FAIL"
        run_cmd = 'show running-config | grep hardware'
        file_cmd = 'show file ' + backup_file + ' | grep hardware'
        conn.execute(run_cmd)
        run_hard = conn.response.strip(run_cmd)
        run_hard_list = hardware_parser(run_hard)
        conn.execute(file_cmd)
        file_hard = conn.response.strip(file_cmd)
        file_hard_list = hardware_parser(file_hard)
        remove_hard = list(set(run_hard_list) - set(file_hard_list))
        if len(remove_hard) != 0:
            cmd = 'configure terminal ; no '
            cmd1 = ('; no ').join(remove_hard)
            cmd2 = cmd + cmd1
            conn.execute(cmd2)
        switch_prompt = conn.get_prompt()
        expected_prompt = 'n]'
        conn.set_prompt(expected_prompt)
        conn.execute('copy bootflash:'+ backup_file +' startup-config ; reload ')
        module_logger.info("%s - Copied backedup config to startup-config and "
                           "triggered reload", threading.current_thread().name)
        conn.set_prompt(switch_prompt)
        conn.send('y\r')
        time.sleep(10)
        update_conn = switch_status(dev_dict)
        dev_dict['conn_obj'] = update_conn
        conn = dev_dict['conn_obj']
        migrate_state['revert_device_conversion'][threading.current_thread().name] = OrderedDict()
        migrate_state['revert_device_conversion'][threading.current_thread().name][
            'overall_status'] = "PASS"
        return dev_dict, migrate_state
    except Exception as err_data:
        module_logger.info("%s - Error while reverting the older config in "
                           "switch", threading.current_thread().name)
        module_logger.debug(err_data)
        migrate_state['revert_device_conversion'][threading.current_thread().name] = OrderedDict()
        migrate_state['revert_device_conversion'][threading.current_thread().name][
            'overall_status'] = "FAIL"
        return dev_dict, migrate_state

def enable_feature_nxapi(conn, lock, migrate_state):
    """ Enabling feature nxapi"""
    global fail_flag
    try:
        span_tree = 'configure terminal ; spanning-tree mode mst'
        conn.execute(span_tree)
        enable_vlan = 'configure terminal ; vlan configuration 1-3967'
        conn.execute(enable_vlan)
        disable_vlan = 'configure terminal ; no spanning-tree vlan 1-3967'
        conn.execute(disable_vlan)
        nxapi_feature = 'configure terminal ; feature nxapi'
        conn.execute(nxapi_feature)
        migrate_state['device_conversion'][threading.current_thread().name][
            'enable_nxapi_feature'] = "PASS"
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while enabling feature nxapi in the "
                            "switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'enable_nxapi_feature'] = "FAIL"
        module_logger.debug(err_data)

def reload_switch(conn, lock, migrate_state):
    """ Reloading the switch"""
    global fail_flag
    try:
        switch_prompt = conn.get_prompt()
        expected_prompt = 'n]'
        conn.set_prompt(expected_prompt)
        conn.execute('copy running-config startup-config ; reload ')
        module_logger.info("%s - Copied running-config to startup-config and "
                           "triggered reload", threading.current_thread().name)
        conn.set_prompt(switch_prompt)
        conn.send('y\r')
        time.sleep(10)
        try:
            conn.execute("show version")
        except:
            pass
        migrate_state['device_conversion'][threading.current_thread().name][
            'reload_switch'] = "PASS"
    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error in reloading the switch", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name][
            'reload_switch'] = "FAIL"
        module_logger.debug(err_data)

def switch_status(dev_dict, upgrade_key=None):
    """Check for switch status"""
    try:
        module_logger.info("%s - Waiting for switch to come up after "
                           "reload", threading.current_thread().name)
        switch_ip = dev_dict["host_name/IP"]
        username = dev_dict["username"]
        password = dev_dict["password"]
        account = Account(username, password)
        conn = SSH2(timeout=300)
        count = 60
        switch_flag = 0
        for _ in xrange(count):
            try:
                conn.connect(switch_ip)
                if conn.response is None:
                    val = conn.login(account, flush=True)
                    conn.execute('term len 0')
                    conn.execute('term width 0')
                    if val is None:
                        module_logger.info("%s - Switch is accessible after "
                                           "reload", threading.current_thread().name)
                        switch_flag = 1
                        break
            except:
                time.sleep(5)
        if switch_flag == 0:
            module_logger.error("%s - Waited for more than 5 "
                                "mins", threading.current_thread().name)
        if switch_flag == 1:
            # Validating upgraded image in switch
            if upgrade_key != None:
                ver_cmd = ""
                image_name = ""
                if "nxos" in dev_dict[upgrade_key].keys():
                    ver_cmd = "sh ver | grep nxos"
                    image_name = dev_dict[upgrade_key]['nxos']
                elif "kickstart" in dev_dict[upgrade_key].keys():
                    ver_cmd = "sh ver | grep kickstart"
                    image_name = dev_dict[upgrade_key]['kickstart']
                conn.execute(ver_cmd)
                if image_name not in conn.response:
                    return conn, 0
            module_logger.info("%s - Getting the switch uptime", threading.current_thread().name)
            for _ in xrange(30):
                up_time = switch_uptime(conn)
                if int(up_time) >= 9:
                    module_logger.info("%s - Switch can be accessed in "
                                       "NDB", threading.current_thread().name)
                    break
                else:
                    time.sleep(20)
                    continue
        if upgrade_key != None:
            return conn, 1
        else:
            return conn
    except Exception as err_data:
        module_logger.error("%s - Error while checking device status",
                            threading.current_thread().name)
        module_logger.debug(err_data)

def switch_uptime(conn):
    """Checks for the switch uptime"""
    try:
        cmd = 'show system uptime'
        conn.execute(cmd)
        minutes = '0'
        pattern = (r"System uptime:\s+(\w+)(\s+)days, "
                   r"(\w+)(\s+)hours, (\w+)(\s+)minutes, (\w+)(\s+)seconds")
        if "System uptime" in conn.response:
            conn.response = conn.response.split("\n\r")
            for line in conn.response:
                match = re.search(pattern, line)
                if match:
                    minutes = match.group(5)
        return minutes
    except Exception as err_data:
        module_logger.error("%s - Error while getting switch uptime",
                            threading.current_thread().name)
        module_logger.debug(err_data)

def revert_nxos(dev_dict):
    """Revert switch configuration"""
    state_dict = {"overall_status": "FAIL"}
    try:
        conn = ""
        switch_ip = dev_dict["host_name/IP"]
        username = dev_dict["username"]
        password = dev_dict["password"]
        account = Account(username, password)
        conn = SSH2(timeout=300)
        conn.connect(switch_ip)
        val = conn.login(account, flush=True)
        if val is None:
            pass
        else:
            count = 60
            switch_flag = 0
            for _ in xrange(count):
                try:
                    conn.connect(switch_ip)
                    if conn.response is None:
                        val = conn.login(account, flush=True)
                        if val is None:
                            switch_flag = 1
                            break
                except:
                    time.sleep(5)
            if switch_flag == 0:
                module_logger.error("%s - Unable to connect while downgrading the switch",
                                threading.current_thread().name)
                return dev_dict, state_dict
        conn.execute('term len 0')
        conn.execute('term width 0')
        version, nxos_flag = get_version(conn)
        dev_dict['nxos_flag'] = nxos_flag
        dev_dict['conn_obj'] = conn
        downgrade_list = [key for key, _ in dev_dict.iteritems() if 'NXOS_Image' in key]
        downgrade_list.sort(reverse=True)
        if len(downgrade_list) > 0:
            del downgrade_list[0]
        if len(downgrade_list) > 0:
            for item in downgrade_list:
                cmd = ''
                switch_prompt = conn.get_prompt()
                expected_prompt = 'n]'
                conn.set_prompt(expected_prompt)                                                 
                if 'nxos' in dev_dict[item].keys():
                    nxos_image = dev_dict[item]['nxos'].strip()
                    module_logger.info("%s - Loading image - %s and waiting for switch"
                                       "to complete installation", threading.current_thread().name,
                                       nxos_image)
                    cmd = 'install all nxos bootflash:' + nxos_image
                else:
                    kickstart_image = dev_dict[item]['kickstart'].strip()
                    system_image = dev_dict[item]['system'].strip()
                    module_logger.info("%s - Loading kickstart image - %s, system image - %s and "
                                       "waiting for switch to complete installation",
                                       threading.current_thread().name, kickstart_image,
                                       system_image)
                    cmd = ('install all kickstart bootflash:' + kickstart_image
                           + ' system bootflash:' + system_image)
                if cmd != '':
                    state_dict[item] = OrderedDict()
                    state_dict[item] = copy.deepcopy(dev_dict[item])
                    conn.execute(cmd)
                    if "Invalid command" in conn.response:
                        module_logger.error("Trying to load invalid image",
                                            threading.current_thread().name)
                        state_dict[item]['downgrade_status'] = 'FAIL'
                    elif "free space in the filesystem is below threshold" in conn.response:
                        module_logger.error("%s - Downgrade failed because of no free space for "
                                            "installation", threading.current_thread().name)
                        state_dict[item]['downgrade_status'] = 'FAIL'
                    else:
                        conn.set_prompt(switch_prompt)
                        conn.send('y\r')                              
                        time.sleep(300)
                        update_conn, upgrade_status = switch_status(dev_dict, item)
                        dev_dict['conn_obj'] = update_conn
                        conn = dev_dict['conn_obj']
                        if upgrade_status:
                            module_logger.info("%s - %s, Downgrade successful",
                                               threading.current_thread().name, item)
                            state_dict[item]['downgrade_status'] = 'PASS'
                        else:
                            module_logger.info("%s - %s, Downgrade failed",
                                               threading.current_thread().name, item)
                            state_dict[item]['downgrade_status'] = 'FAIL'
        cmd = ''
        if 'nxos' in dev_dict['switch_image'].keys():
            nxos_image = dev_dict['switch_image']['nxos'].strip()
            module_logger.info("%s - Loading image - %s and waiting for switch to complete "
                               "installation", threading.current_thread().name, nxos_image)
            cmd = 'install all nxos bootflash:' + nxos_image
        else:
            kickstart_image = dev_dict['switch_image']['kickstart'].strip()
            system_image = dev_dict['switch_image']['system'].strip()
            module_logger.info("%s - Loading kickstart image - %s, system image - %s and waiting "
                               "for switch to complete installation",
                               threading.current_thread().name, kickstart_image, system_image)
            cmd = ('install all kickstart bootflash:' + kickstart_image
                   + ' system bootflash:' + system_image)
        if cmd != '':
            switch_prompt = conn.get_prompt()
            expected_prompt = 'n]'
            conn.set_prompt(expected_prompt)
            state_dict["switch_image"] = OrderedDict()
            state_dict["switch_image"] = copy.deepcopy(dev_dict['switch_image'])
            conn.execute(cmd)
            if "Invalid command" in conn.response:
                module_logger.error("Trying to load invalid image")
            else:
                conn.set_prompt(switch_prompt)
                conn.send('y\r')                              
                time.sleep(300)
                update_conn, upgrade_status = switch_status(dev_dict, 'switch_image')
                dev_dict['conn_obj'] = update_conn
                conn = dev_dict['conn_obj']
                if upgrade_status:
                    module_logger.info("%s - switch_image, Downgrade successful",
                                       threading.current_thread().name)
                    state_dict["switch_image"]['downgrade_status'] = 'PASS'
                else:
                    module_logger.info("%s - switch_image, Downgrade failed",
                                       threading.current_thread().name)
                    state_dict["switch_image"]['downgrade_status'] = 'FAIL'
        state_dict["overall_status"] = "PASS"
        for item in state_dict:
            if 'NXOS_Image' in item or 'switch_image' in item:
                if state_dict[item]['downgrade_status'] == "FAIL":
                    state_dict["overall_status"] = "FAIL"
                    break
        return dev_dict, state_dict
    except Exception as err_data:
        module_logger.error("%s - Error while downgrading the switch",
                            threading.current_thread().name)
        module_logger.debug(err_data)
        return dev_dict, state_dict

def upgrade_switch(dev_dict):
    """Upgrade switch NX-OS image"""
    state_dict = {"overall_status": "FAIL"}
    global upgrade_fail_flag
    try:
        conn = ""
        switch_ip = dev_dict["host_name/IP"]
        username = dev_dict["username"]
        password = dev_dict["password"]
        account = Account(username, password)
        conn = SSH2(timeout=300)
        conn.connect(switch_ip)
        val = conn.login(account, flush=True)
        if val is None:
            pass
        else:
            count = 60
            switch_flag = 0
            for _ in xrange(count):
                try:
                    conn.connect(switch_ip)
                    if conn.response is None:
                        val = conn.login(account, flush=True)
                        if val is None:
                            switch_flag = 1
                            break
                except:
                    time.sleep(5)
            if switch_flag == 0:
                module_logger.error("%s - Unable to connect while upgrading the switch",
                                threading.current_thread().name)
                return dev_dict, state_dict
        conn.execute('term len 0')
        conn.execute('term width 0')
        version, nxos_flag = get_version(conn)
        dev_dict['nxos_flag'] = nxos_flag
        dev_dict['conn_obj'] = conn
        upgrade_list = [key for key, _ in dev_dict.iteritems() if 'NXOS_Image' in key]
        upgrade_list.sort()
        dev_dict['switch_image'] = get_current_image(dev_dict)
        module_logger.info("%s - current image - %s", threading.current_thread().name,
                           dev_dict['switch_image'])
        state_dict["switch_image"] = OrderedDict()
        state_dict["switch_image"] = copy.deepcopy(dev_dict['switch_image'])
        if len(upgrade_list) > 0:
            for item in upgrade_list:
                cmd = ''
                switch_prompt = conn.get_prompt()
                expected_prompt = 'n]'
                conn.set_prompt(expected_prompt)                                 
                if 'nxos' in dev_dict[item].keys():
                    if 'nxos' in dev_dict['switch_image'].keys() and dev_dict[item]['nxos'] \
                    in dev_dict['switch_image']['nxos']:
                        pass
                    else:
                        module_logger.info("%s - Loading image - %s and waiting for switch to "
                                           "complete installation",
                                           threading.current_thread().name, dev_dict[item]['nxos'])
                        cmd = 'install all nxos bootflash:' + dev_dict[item]['nxos']
                else:
                    if ('kickstart' in dev_dict['switch_image'].keys() and \
                    dev_dict[item]['kickstart'] in dev_dict['switch_image']['kickstart'])\
                    and ('system' in dev_dict['switch_image'].keys() and dev_dict[item]['system'] \
                    in dev_dict['switch_image']['system']):
                        pass
                    else:
                        module_logger.info("%s - Loading kickstart image - %s, system image - %s "
                                           "and waiting for switch to complete installation",
                                           threading.current_thread().name,
                                           dev_dict[item]['kickstart'], dev_dict[item]['system'])
                        cmd = ('install all kickstart bootflash:' + dev_dict[item]['kickstart']
                               + ' system bootflash:' + dev_dict[item]['system'])
                if cmd != '':
                    state_dict[item] = OrderedDict()
                    state_dict[item] = copy.deepcopy(dev_dict[item])
                    conn.execute(cmd)
                    if "Invalid command" in conn.response:
                        upgrade_fail_flag = True
                        module_logger.error("Trying to load invalid image %s", conn.response)
                        module_logger.info("%s - %s, upgrade failed",
                                           threading.current_thread().name, item)
                        state_dict[item]['upgrade_status'] = 'FAIL'
                        upgrade_fail_flag = True
                    elif "free space in the filesystem is below threshold" in conn.response:
                        module_logger.error("%s - Upgrade failed because of no free space for "
                                            "installation", threading.current_thread().name)
                        module_logger.info("%s - %s, upgrade failed",
                                           threading.current_thread().name, item)
                        state_dict[item]['upgrade_status'] = 'FAIL'
                        upgrade_fail_flag = True
                    else:
                        conn.set_prompt(switch_prompt)
                        conn.send('y\r')                              
                        time.sleep(300)
                        update_conn, upgrade_status = switch_status(dev_dict, item)
                        dev_dict['conn_obj'] = update_conn
                        conn = dev_dict['conn_obj']
                        if upgrade_status:
                            module_logger.info("%s - %s, upgrade successful",
                                               threading.current_thread().name, item)
                            state_dict[item]['upgrade_status'] = 'PASS'
                        else:
                            module_logger.info("%s - %s, upgrade failed",
                                               threading.current_thread().name, item)
                            upgrade_fail_flag = True
                            state_dict[item]['upgrade_status'] = 'FAIL'
        state_dict["overall_status"] = "PASS"
        for item in state_dict:
            if 'NXOS_Image' in item:
                if state_dict[item]['upgrade_status'] == "FAIL":
                    state_dict["overall_status"] = "FAIL"
                    break
        return dev_dict, state_dict

    except Exception as err_data:
        upgrade_fail_flag = True
        module_logger.error("%s - Error while upgrading NX-OS image in a switch",
                            threading.current_thread().name)
        module_logger.debug(err_data)
        return dev_dict, state_dict

def backup_config(conn, version, file_name, lock):
    """ Taking the backup config"""
    global fail_flag
    try:
        file_name = file_name
        conn.execute('dir | grep ' + file_name)
        dir_content = conn.response.strip('dir | grep ' + file_name)
        list_of_files = dir_content.split('\n')
        for line in list_of_files:
            if file_name in line:
                dir_file = line.split()[-1]
                dir_file = dir_file.strip()
                if file_name == dir_file:
                    if 'U' not in version:
                        switch_prompt = conn.get_prompt()
                        expected_prompt = 'y]'
                        conn.set_prompt(expected_prompt)
                        conn.execute('del ' + file_name)
                        conn.set_prompt(switch_prompt)
                        conn.send('y\r')
                    else:
                        conn.execute('del ' + file_name)
                break
        conn.execute('copy running-config ' + file_name)
        conn.execute('dir | grep ' + file_name)
        dir_content = conn.response.strip('dir | grep ' + file_name)
        if file_name in dir_content:
            module_logger.info("%s - Successfully created backup of configuration file in "
                               "switch", threading.current_thread().name)

    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while copying running config to backup config file in "
                            "switch", threading.current_thread().name)
        module_logger.debug(err_data)

def openflow_to_nxapi(dev_dict, hardware_dict, lock, migrate_state, backup_file):
    """ Converting openflow to nxapi"""
    global fail_flag
    try:
        switch_ip = dev_dict["host_name/IP"]
        username = dev_dict["username"]
        password = dev_dict["password"]
        rerun_flag = 0
        check_state = {}
        if 'device_conversion' in migrate_state.keys():
            if switch_ip in migrate_state['device_conversion'].keys():
                check_state = copy.deepcopy(migrate_state['device_conversion'][switch_ip])
                rerun_flag = 1
        else:
            migrate_state['device_conversion'] = OrderedDict()
        switch_ova = ""
        if "ofa_ova_name" in dev_dict.keys():
            switch_ova = dev_dict["ofa_ova_name"]
        account = Account(username, password)
        conn = SSH2(timeout=300)
        conn.connect(switch_ip)
        module_logger.info("%s - Trying to login %s", threading.current_thread().name, switch_ip)
        val = conn.login(account, flush=True)
        if val is None:
            module_logger.info("%s - Login success", threading.current_thread().name)
        conn.execute('term len 0')
        conn.execute('term width 0')
        dev_dict['conn_obj'] = conn
        platform = get_platform(conn, lock)
        dev_dict['platform'] = platform
        version, nxos_flag = get_version(conn, lock)
        dev_dict['nxos_flag'] = nxos_flag
        dev_dict['version'] = version
        if rerun_flag == 0:
            module_logger.info("%s - Switch Platform %s", threading.current_thread().name, platform)
            module_logger.info("%s - Switch Version %s", threading.current_thread().name, version)
            backup_config(conn, version, backup_file, lock)
            # Check for Openflow configuration on switch
        module_logger.debug("%s - Calling check_openflow_conf()", threading.current_thread().name)
        openflow_flag = check_openflow_conf(conn, lock)
        module_logger.debug("%s - Openflow conf %s", threading.current_thread().name,
                            openflow_flag)
        if rerun_flag == 0:
            migrate_state['device_conversion'][threading.current_thread().name] = OrderedDict()
        if 'package_name' not in migrate_state['device_conversion'][switch_ip].keys():
            if switch_ova != '':
                pkg_name = remove_virtualsevice(conn, lock, switch_ova)
                conn.execute('copy running-config startup-config')
                dev_dict['pkg_name'] = pkg_name
                migrate_state['device_conversion'][threading.current_thread().name]['package_name'] = copy.deepcopy(pkg_name)
        if openflow_flag is True:
            if ('remove_openflow_config' not in check_state.keys()
                    or ('remove_openflow_config' in check_state.keys() and check_state['remove_openflow_config'] == 'FAIL')):
                # Remove those configuration by running no openflow command
                module_logger.debug("%s - Calling remove_openflow_conf()",
                                    threading.current_thread().name)
                remove_openflow_conf(conn, lock, version, migrate_state)
                conn.execute('copy running-config startup-config')
                module_logger.info("%s - Removed openflow configurations",
                                   threading.current_thread().name)
            if ('remove_interface_config' not in check_state.keys()
                    or ('remove_interface_config' in check_state.keys() and check_state['remove_interface_config'] == 'FAIL')):
                # Make the interface to default using default commands
                module_logger.debug("%s - Calling remove_interface_conf()",
                                    threading.current_thread().name)
                remove_interface_conf(conn, lock, migrate_state)
                conn.execute('copy running-config startup-config')
            if ('remove_hardware_config' not in check_state.keys()
                    or ('remove_hardware_config' in check_state.keys() and check_state['remove_hardware_config'] == 'FAIL')):
                # Check for openflow hardware configuration and remove it
                module_logger.debug("%s - Calling remove_openflow_hard()",
                                    threading.current_thread().name)
                remove_openflow_hard(conn, lock, migrate_state)
                conn.execute('copy running-config startup-config')
        if ('enable_nxapi_feature' not in check_state.keys()
                or ('enable_nxapi_feature' in check_state.keys() and check_state['enable_nxapi_feature'] == 'FAIL')):
            module_logger.info("%s - Enabling feature nxapi", threading.current_thread().name)
            enable_feature_nxapi(conn, lock, migrate_state)
            conn.execute('copy running-config startup-config')
        if ('add_nxapi_hardwareconfig' not in check_state.keys()
                    or ('add_nxapi_hardwareconfig' in check_state.keys() and check_state['add_nxapi_hardwareconfig'] == 'FAIL')):
            module_logger.info("%s - Adding NXAPI hardware configs", threading.current_thread().name)
            add_nxapi_hard(conn, lock, str(platform),
                           dev_dict, hardware_dict['HADWARE_CMDS_TO_PLATFORMS'], migrate_state)
            conn.execute('copy running-config startup-config')
        key_list = dev_dict.keys()
        sub = 'NXOS_Image'
        if not any(sub in mystring for mystring in key_list):
            reload_switch(conn, lock, migrate_state)
            update_conn = switch_status(dev_dict)
            dev_dict['conn_obj'] = update_conn
        return dev_dict, migrate_state

    except Exception as err_data:
        lock.acquire()
        fail_flag = True
        lock.release()
        module_logger.error("%s - Error while converting openflow to "
                            "nxapi", threading.current_thread().name)
        migrate_state['device_conversion'][threading.current_thread().name] = OrderedDict()
        migrate_state['device_conversion'][threading.current_thread().name][
            'overall_status'] = "FAIL"
        module_logger.debug(err_data)
        return dev_dict, migrate_state
