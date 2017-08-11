from subprocess import call, PIPE, STDOUT
import os
import time
import yaml
import pexpect
import sys
import fileinput
import paramiko
import logging
import pdb

class Device:
    def __init__(self):
        self.ip_l = []
        self.cp_keypem_res = ""
        self.tem_serpath = ""
        self.cp_cert_speloc_res = ""
        self.prov_pass = ""
        self.sethttps = ""
        self.cp_cert_lhser = ""
        self.login_mulser = ""
        self.tem_seruser = ""
        self.pass_pro_res = ""
        self.temp_pass = ""
        self.copy_keyfile = ""
        self.append_forwkey = ""
        self.prov_pass_b = ""
        self.device_password_list = []
        self.gen_cert_key = ""
        self.log_mul_dev = 0
        self.pass_pro = ""
        self.cp_cert_lhser_res = ""
        self.temp_user = ""
        self.temp_ip = ""
        self.temp_dport = ""
        self.cp_certpem_res = ""
        self.copy_file = 1
        self.capem_sw_res = ""
        self.server_password_list = []
        self.device_user_list = []
        self.cp_keypem = ""
        self.cp_xncpem = ""
        self.cp_xncpem_re = ""
        self.cp_certpem = ""
        self.password = ""
        self.cp_ser_speloc = ""
        self.default_bits_str = ""
        self.gen_cert_key_result = ""
        self.tem_serip = ""
        self.cp_certfile = ""
        self.sw_tlstrust_res = ""
        self.cp_cert_speloc = ""
        self.run_ndb = ""
        self.default_days_str = ""
        self.server_path_list = []
        self.gen_key_ca_files_result = ""
        self.cp_key_lhser = ""
        self.copy_keystore_res = ""
        self.sw_tlstrust = ""
        self.cp_trust_res = ""
        self.path = ""
        self.capem_sw = ""
        self.server_ip_list = []
        self.cp_key_lhser_res = ""
        self.cp_trust = ""
        self.copy_keystore = ""
        self.gen_key_ca = ""
        self.server_user_list = []
        self.temp_serpass = ""
        self.xncp_tlskey = ""
        self.app_forwkey_e = ""
        self.run_n = ""
        self.ip = ""
        self.user = ""
        self.xncp_tlskey_res = ""
        self.cp_ser_speloc_res = ""
        self.device_ip_list = []
        self.device_user_list = []
        self.device_password_list = []
        self.device_port_list = []
        self.password = ""
        self.server_path = ""
        self.user = ""
        self.path = ""
        all_ips_from_yaml = []
        self.replace_ip = 0
        self.organization_name_c = ""
        self.organization_name = ""
        self.state_name_c = ""
        self.state_name = ""
        self.country_name_c = ""
        self.countryname = ""
        self.emailaddress_c = ""
        self.email_address = ""
        self.localityname_c = ""
        self.locality_name = ""
        self.organizationalunit_name_c = ""
        self.organizational_unit_name = ""
        self.commonname_c = ""
        self.common_name = ""
        self.ip_list = ""
        self.ip1_list = ""
        self.ip2_list = ""
        self.ip3_list = ""
        self.ip4_list = ""
        self.ip5_list = ""
        self.ip6_list = ""
        self.ip7_list = ""
        self.ip8_list = ""
        self.ip9_list = ""
        self.ip10_list = ""
        self.all_ips_from_yaml = []
        self.ip_l1 = ""
        self.ip_l2 = ""
        self.ip_l3 = ""
        self.ip_l4 = ""
        self.ip_l5 = ""
        self.ip_l6 = ""
        self.ip_l7 = ""
        self.ip_l8 = ""
        self.ip_l9 = ""
        self.ip_l10 = ""
        self.append_config = 0
        self.default_md_c = ""
        self.cp_xncpem_res = ""
        self.organizationalunit_name_list = ""
        self.localityname_list = ""
        self.default_days = ""
        self.default_md = ""
        self.organizationname_list = ""
        self.default_md_list = []
        self.state_name_list = ""
        self.default_bits_c = ""
        self.server_port_list = []
        self.default_bits_list = []
        self.country_name_list = ""
        self.keystore_password = ""
        self.default_days_c = ""
        self.emailaddress_list = ""
        self.default_bits = ""
        self.commonname_list = ""
        self.xnc_pwd = ""
        self.xnc_usr = ""
    def method_one(self):
        try:
            with open("./Utilities/TlsCerts/ca.conf", 'r') as fil_ptr:
                for line in fil_ptr:
                    if 'default_days' in line:
                        self.default_days_c = line.split(" ")[-1]
                        self.default_days_c = self.default_days_c.strip()
                    if 'default_md' in line and 'digest' in line:
                        line1 = line.strip()
                        self.default_md_list = line1.split(" ")
                        self.default_md_list = filter(None, \
                                                    self.default_md_list)
                        self.default_md_c = self.default_md_list[2]
                    if 'default_bits' in line and 'Size of keys' in line:
                        line2 = line.strip()
                        self.default_bits_list = line2.split(" ")
                        self.default_bits_list = filter(None,\
                                                     self.default_bits_list)
                        self.default_bits_c = self.default_bits_list[2]
                    if 'commonName_default' in line:
                        self.commonname_list = line.split(" ")[-1]
                        self.commonname_c = self.commonname_list.strip()
                    if 'organizationName_default' in line:
                        self.organizationname_list = line.split(" ")[-1]
                        self.organization_name_c = \
                        self.organizationname_list.strip()
                    if 'localityName_default' in line:
                        self.localityname_list = line.split(" ")[-1]
                        self.localityname_c = self.localityname_list.strip()
                    if 'stateOrProvinceName_default' in line:
                        self.state_name_list = line.split(" ")[-1]
                        self.state_name_c = \
                        self.state_name_list.strip()
                    if 'countryName_default' in line:
                        self.country_name_list = line.split(" ")[-1]
                        self.country_name_c = self.country_name_list.strip()
                    if 'emailAddress_default' in line:
                        self.emailaddress_list = line.split(" ")[-1]
                        self.emailaddress_c = self.emailaddress_list.strip()
                    if 'organizationalUnitName_default' in line:
                        self.organizationalunit_name_list = line.split(" ")[-1]
                        self.organizationalunit_name_c = \
                        self.organizationalunit_name_list.strip()
                    if 'IP.1' and '1.1.1.1' in line:
                        self.ip_list = line.split(" ")[-1]
                        self.ip_l1 = self.ip_list.strip()
                        self.ip_l.append(self.ip_l1)
                    if 'IP.2' in line:
                        self.ip2_list = line.split(" ")[-1]
                        self.ip_l2 = self.ip2_list.strip()
                        self.ip_l.append(self.ip_l2)
                    if 'IP.3' in line:
                        self.ip3_list = line.split(" ")[-1]
                        self.ip_l3 = self.ip3_list.strip()
                        self.ip_l.append(self.ip_l3)
                    if 'IP.4' in line:
                        self.ip4_list = line.split(" ")[-1]
                        self.ip_l4 = self.ip4_list.strip()
                        self.ip_l.append(self.ip_l4)
                    if 'IP.5' in line:
                        self.ip5_list = line.split(" ")[-1]
                        self.ip_l5 = self.ip5_list.strip()
                        self.ip_l.append(self.ip_l5)
                    if 'IP.6' in line:
                        self.ip6_list = line.split(" ")[-1]
                        self.ip_l6 = self.ip6_list.strip()
                        self.ip_l.append(self.ip_l6)
                    if 'IP.7' in line:
                        self.ip7_list = line.split(" ")[-1]
                        self.ip_l7 = self.ip7_list.strip()
                        self.ip_l.append(self.ip_l7)
                    if 'IP.8' in line:
                        self.ip8_list = line.split(" ")[-1]
                        self.ip_l8 = self.ip8_list.strip()
                        self.ip_l.append(self.ip_l8)
                    if 'IP.9' in line:
                        self.ip9_list = line.split(" ")[-1]
                        self.ip_l9 = self.ip9_list.strip()
                        self.ip_l.append(self.ip_l9)
                    if 'IP.10' in line:
                        self.ip10_list = line.split(" ")[-1]
                        self.ip_l10 = self.ip10_list.strip()
                        self.ip_l.append(self.ip_l10)
        except OSError:
            LOGGER.error("Failed to open configuration file")
            sys.exit(0)
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.load(file_ptr)
                self.default_days = confi['default_days']
                self.default_md = confi['default_md']
                self.default_bits = confi['default_bits']
                self.countryname = confi['countryName']
                self.state_name = confi['stateOrProvinceName']
                self.organization_name = confi['organizationName']
                self.organizational_unit_name = confi['organizationalUnitName']
                self.common_name = confi['commonName']
                self.email_address = confi['emailAddress']
                self.locality_name = confi['localityName']
                self.keystore_password = str(confi['keystore'])
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        def replace_method(file1, searchexp, replaceexp):
            for line in fileinput.input(file1, inplace=1):
                try:
                    if searchexp in line:
                        line = line.replace(searchexp, replaceexp)
                        LOGGER.info("Replace value - "+str(replaceexp)+\
                                " in config file is success")
                    try:
                        sys.stdout.write(line)
                    except OSError:
                        LOGGER.error("Failed to replace value "+\
                        +str(replaceexp)+" in config file")
                except OSError:
                    LOGGER.error("Failed to replace values in config file")
        replace_method("./Utilities/TlsCerts/ca.conf", \
            self.organization_name_c, str(self.organization_name))
        replace_method("./Utilities/TlsCerts/ca.conf", self.state_name_c, \
        str(self.state_name))
        replace_method("./Utilities/TlsCerts/ca.conf", self.country_name_c, \
        str(self.countryname))
        replace_method("./Utilities/TlsCerts/ca.conf", self.emailaddress_c, \
        str(self.email_address))
        replace_method("./Utilities/TlsCerts/ca.conf", self.localityname_c, \
        str(self.locality_name))
        replace_method("./Utilities/TlsCerts/ca.conf", \
        self.organizationalunit_name_c, str(self.organization_name))
        replace_method("./Utilities/TlsCerts/ca.conf", self.commonname_c, \
        str(self.common_name))
        replace_method("./Utilities/TlsCerts/ca.conf", self.default_md_c, \
        str(self.default_md))
        replace_method("./Utilities/TlsCerts/ca.conf", self.default_bits_c, \
        str(self.default_bits))
        self.all_ips_from_yaml = sorted(confi['IP'].keys())
        for val in self.all_ips_from_yaml:
            self.device_ip_list.append(confi['IP'][val]['address'])
            self.device_user_list.append(confi['IP'][val]['username'])
            self.device_password_list.append(confi['IP'][val]['password'])
            self.device_port_list.append(confi['IP'][val]['port'])  
        self.replace_ip = 0
        while self.replace_ip < len(self.device_ip_list):
            replace_method("./Utilities/TlsCerts/ca.conf", \
                self.ip_l[self.replace_ip],\
                str(self.device_ip_list[self.replace_ip]))
            self.replace_ip += 1
        self.default_days_str = str(self.default_days)
        self.default_bits_str = str(self.default_bits)
    def method_two(self):
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.load(file_ptr)
                self.keystore_password = str(confi['keystore'])
        except OSError:
            LOGGER.error("Failed to open input yaml file")
        self.gen_key_ca = str("openssl req -x509 -nodes -days "+\
                              self.default_days_str+"0 -newkey rsa:"+
                              self.default_bits_str+" -out "+\
                              "./Utilities/TlsCerts/"+\
                              "mypersonalca/certs/ca.pem \
                              -outform PEM -keyout ./Utilities/TlsCerts/"+\
                              "mypersonalca/private/ca.key -batch")
        try:
            self.gen_key_ca_files_result = call(self.gen_key_ca, \
                                           shell=True, \
                                           stdout=PIPE, \
                                           stderr=STDOUT)
            if self.gen_key_ca_files_result == 0:
                LOGGER.info("Generate ca.pem and ca.key files success")
            else:
                LOGGER.error("Failed to Generate ca.pem and "+\
                "ca.key files -step5")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate ca.pem and ca.key files -step4")
            sys.exit(0)
        self.gen_cert_key = str("openssl req -new -x509 -days "+\
                            self.default_days_str+" -nodes -out "+\
                            "./Utilities/TlsCerts/server.crt -keyout "+\
                            "./Utilities/TlsCerts/server.key -config "+\
                            "./Utilities/TlsCerts/ca.conf -batch")
        try:
            self.gen_cert_key_result = call(self.gen_cert_key, \
                                       shell=True, \
                                           stdout=PIPE, \
                                           stderr=STDOUT)
            if self.gen_cert_key_result == 0:
                LOGGER.info("Generate server.crt and server.key files success")
            else:
                LOGGER.error("Failed to Generate server.crt and server.key"+\
                " files -step5")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate ca.pem and ca.key files -step4")
            sys.exit(0)
        self.ip = confi['ServerIP']['ServerIP1']['ip']
        self.user = confi['ServerIP']['ServerIP1']['user']
        self.password = confi['ServerIP']['ServerIP1']['password']
        self.path = confi['ServerIP']['ServerIP1']['path_ndb_build']
        try:
            self.port = confi['ServerIP']['ServerIP1']['port']
        except KeyError:
            self.port = 0
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
        self.server_path_list = []
        self.server_port_list = []
        server_list = sorted(confi['ServerIP'].keys())
        for value in server_list:
            self.server_ip_list.append(confi['ServerIP']\
                    [value]['ip'])
            self.server_user_list.append(confi['ServerIP']\
                    [value]['user'])
            self.server_password_list.append(confi['ServerIP']\
                    [value]['password'])
            self.server_path_list.append(confi['ServerIP']\
                    [value]['path_ndb_build'])
            str(self.server_password_list)
            try:
                self.server_port_list.append(confi['ServerIP']\
                    [value]['port'])
            except KeyError:
                self.server_port_list.append(0)
        self.append_forwkey = 0
        while self.append_forwkey < len(self.server_path_list):
            suffix = "/"
            self.server_path = str(self.server_path_list\
                              [self.append_forwkey])
            if self.server_path.endswith(suffix) == False:
                try:
                    self.server_path = self.server_path+"/"
                    self.server_path_list[self.append_forwkey] \
                        = str(self.server_path)
                except OSError:
                    LOGGER.error("Failed to append forward slash"+\
                        " at end to provided NDB path")
            self.append_forwkey += 1
        self.app_forwkey_e = 0
        while self.app_forwkey_e < len(self.server_path_list):
            suffix = "/"
            self.server_path = str(self.server_path_list\
                              [self.app_forwkey_e])
            if self.server_path.startswith(suffix) == False:
                try:
                    self.server_path = "/"+self.server_path
                    self.server_path_list[self.app_forwkey_e] = \
                       str(self.server_path)
                except OSError:
                    LOGGER.error("Failed to append forward slash"+\
                        " at start to provided NDB path")
            self.app_forwkey_e += 1
        self.append_config = 0
        while self.append_config < len(self.server_path_list):
            suffix = "configuration"+"/"
            self.server_path = str(self.server_path_list\
                              [self.append_config])
            if self.server_path.endswith(suffix) == False:
                try:
                    self.server_path = self.server_path+"configuration"+"/"
                    self.server_path_list[self.append_config] \
                        = str(self.server_path)
                except OSError:
                    LOGGER.error("Failed to append configuration"+\
                        " string to provided NDB path")
            self.append_config += 1
        self.ip = self.server_ip_list[0]
        self.user = self.server_user_list[0]
        self.password = self.server_password_list[0]
        self.path = self.server_path_list[0]
        self.port = self.server_port_list[0]
        if self.port != 0:
            try:
                ssh = paramiko.SSHClient()
                server = self.ip
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server, port=self.port, username=self.user, password=self.password)
                sftp = ssh.open_sftp()
                localpath = './Utilities/TlsCerts/server.crt'
                remotepath = '/root/xnc/configuration/server.crt'
                sftp.put(localpath, remotepath)
                local = './Utilities/TlsCerts/server.key'
                remote = '/root/xnc/configuration/server.key'
                sftp.put(local, remote)
                sftp.close()
            except:
                LOGGER.error("Error while ssh into the server")
                sys.exit(0)
        else:
            try:
                ssh = paramiko.SSHClient()
                server = self.ip
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server, username=self.user, password=self.password)
                sftp = ssh.open_sftp()
                localpath = './Utilities/TlsCerts/server.crt'
                remotepath = self.path+'server.crt'
                sftp.put(localpath, remotepath)
                local = './Utilities/TlsCerts/server.key'
                remote = self.path+'server.key'
                sftp.put(local, remote)
                sftp.close()
            except:
                LOGGER.error("Error while ssh into the server")
                exit(0)
        """
        if self.copy_file == 1:
            if self.port != 0:
                try:
                    ssh = paramiko.SSHClient()
                    server = self.ip
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(server, port=self.port, username=self.user, password=self.password)
                    sftp = ssh.open_sftp()
                    localpath = './Utilities/TlsCerts/server.key'
                    remotepath = '/root/xnc/server.key'
                    sftp.put(localpath, remotepath)
                    sftp.close()
                    ssh.close()
                except paramiko.SSHException:
                    LOGGER.error("Error while ssh into the device5")
            else:
                pass
        else:
            self.cp_ser_speloc = "cp -r ./Utilities/TlsCerts/server.key "+\
                                    self.path
            self.cp_ser_speloc_res = call(str(self.cp_ser_speloc), shell=True)
            self.cp_cert_speloc = "cp -r ./Utilities/TlsCerts/server.crt "+\
                                    self.path
            self.cp_cert_speloc_res = call(str(self.cp_cert_speloc), \
                                    shell=True)
        """
        while(self.log_mul_dev < len(self.device_ip_list)):
            self.temp_ip = self.device_ip_list[self.log_mul_dev]
            self.temp_user = self.device_user_list[self.log_mul_dev]
            self.temp_pass = self.device_password_list[self.log_mul_dev]
            self.temp_dport = self.device_port_list[self.log_mul_dev]
            child = pexpect.spawn('telnet '+ self.temp_ip)
            time.sleep(3)
            try:
                child.expect('login: ')
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Device is not reachable")
                sys.exit(0)
            child.sendline(self.temp_user)
            time.sleep(3)
            try:
                child.expect('assword: ')
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Login incorrect Provided User name is not correct")
                sys.exit(0)
            child.sendline(self.temp_pass)
            time.sleep(3)
            try:
                child.expect("#")
                LOGGER.info("Device "+str(self.temp_ip)+\
                    " Login success")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Login incorrect Provided Password is not correct")
                sys.exit(0)
            child.sendline("configure terminal")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure in device using configuration "+\
                    "terminal command")
            child.sendline("feature nxapi")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure feature "+\
                    "nxapi command in device")
            #pdb.set_trace()
            child.sendline("feature sftp-server")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure feature "+\
                    "sftp-server command in device")
            self.sethttps = str("nxapi https port "+str(self.temp_dport))
            child.sendline(self.sethttps)
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to set https port "+\
                    "with provided value in device")
            try:
                child.logfile = open("./Utilities/TlsCerts/temp/temp.log", "w")
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            child.sendline("dir bootflash:server.key")
            try:
                with open("./Utilities/TlsCerts/temp/temp.log", "r") as fp:
                    for line in fp:
                        if "server.key" in line:
                            child.sendline("delete bootflash:server.key")
                            child.expect("[y]")
                            child.sendline("y")
                            break
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            child.sendline("dir bootflash:server.crt")
            try:
                with open("./Utilities/TlsCerts/temp/temp.log", "r") as fp1:
                    for line1 in fp1:
                        if "server.crt" in line1:
                            child.sendline("delete bootflash:server.crt")
                            child.expect("[y]")
                            child.sendline("y")
                            break
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            """
            if self.port != 0:
                ssh = paramiko.SSHClient()
                server = self.temp_ip
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(server, username=self.temp_user, \
                        password=self.temp_pass)
                    sftp = ssh.open_sftp()
                    localpath = './Utilities/TlsCerts/server.key'
                    remotepath = 'server.key'
                    sftp.put(localpath, remotepath)
                except paramiko.SSHException:
                    LOGGER.error("Error while ssh into the device1")
                    sys.exit(0)
            else:
                ssh = paramiko.SSHClient()
                server = self.temp_ip
                #try:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server, username=self.temp_user, \
                    password=self.temp_pass)
                sftp = ssh.open_sftp()
                localpath = './Utilities/TlsCerts/server.key'
                remotepath = 'server.key'
                sftp.put(localpath, remotepath)
                #except paramiko.SSHException:
                #    LOGGER.error("Error while ssh into the device2")
                 #   sys.exit(0)
            if self.port != 0:
                try:
                    time.sleep(10)
                    localpath = './Utilities/TlsCerts/server.crt'
                    remotepath = 'server.crt'
                    sftp.put(localpath, remotepath)
                    sftp.close()
                    ssh.close()
                except paramiko.SSHException:
                    LOGGER.error("Error while ssh into the device")
                    sys.exit(0)
            else:
                try:
                    localpath = './Utilities/TlsCerts/server.crt'
                    remotepath = 'server.crt'
                    sftp.put(localpath, remotepath)
                    sftp.close()
                    ssh.close()
                except paramiko.SSHException:
                    pass
            """
            self.copy_keyfile = str("copy scp://"+self.user+'@'+\
                self.ip+self.path+"server.key "+
                "bootflash:/// vrf management")
            child.sendline(self.copy_keyfile)
            try:
                child.expect ("continue")
                child.sendline ("yes")
                try:
                    child.expect('assword: ')
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided User name is not correct")
                    sys.exit(0)
                child.sendline (self.password)
                try:
                    child.expect("#")
                    LOGGER.info("Device "+str(self.temp_ip)+\
                        " copy server.key file success")
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided Password is not correct")
                    sys.exit(0)
            except:
                try:
                    child.expect('assword: ')
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided User name is not correct")
                    sys.exit(0)
                child.sendline (self.password)
                try:
                    child.expect("#")
                    LOGGER.info("Device "+str(self.temp_ip)+\
                        " copy server.key file success")
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided Password is not correct")
                    sys.exit(0)
            time.sleep(10)
            self.cp_certfile = str("copy scp://"+self.user+'@'+\
                self.ip+self.path+"server.crt bootflash:/// vrf management")
            child.sendline(self.cp_certfile)
            try:
                child.expect ("continue")
                child.sendline ("yes")
                try:
                    child.expect('assword: ')
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided User name is not correct")
                    sys.exit(0)
                child.sendline (self.password)
                try:
                    child.expect("#")
                    LOGGER.info("Device "+str(self.temp_ip)+\
                        "  copy server.crt file success")
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided Password is not correct")
                    sys.exit(0)
            except:
                try:
                    child.expect('assword: ')
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided User name is not correct")
                    sys.exit(0)
                child.sendline (self.password)
                try:
                    child.expect("#")
                    LOGGER.info("Device "+str(self.temp_ip)+\
                        " copy server.crt file success")
                except pexpect.ExceptionPexpect:
                    LOGGER.error("Device "+str(self.temp_ip)+\
                        " Login incorrect Provided Password is not correct")
                    sys.exit(0)
            time.sleep(10)
            child.sendline("configure terminal")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure in device using configuration "+\
                    "terminal command")
            time.sleep(5)
            child.sendline("nxapi certificate httpskey "+
            	"keyfile bootflash:///server.key")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure certificate keyfile "+\
                    "in device using nxapi certificate httpskey keyfile "+\
                    "bootflash:///server.key command")
            time.sleep(5)
            try:
                with open("./Utilities/TlsCerts/temp/temp.log", "r") as fp4:
                    for line4 in fp4:
                        time.sleep(5)
                        if "done" and "Upload" and" done" \
                            and "cert" and "key" and "match" in line4:
                            break
                        else:
                            child.sendline("nxapi certificate "+
                            	"httpskey keyfile bootflash:///server.key")
                            child.expect('#')
                            break
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            child.sendline("nxapi certificate httpscrt"+ \
            	" certfile bootflash:///server.crt")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure certificate certfile "+\
                    "in device using nxapi certificate httpscrt certfile "+\
                    "bootflash:///server.crt command")
            time.sleep(5)
            try:
                with open("./Utilities/TlsCerts/temp/temp.log", "r") as fp5:
                    for line5 in fp5:
                        time.sleep(5)
                        if "done" and "Upload" and" done" and "cert" \
                            and "key" and "match" in line4:
                            break
                        else:
                            child.sendline("nxapi certificate "+\
                            	"httpscrt certfile bootflash:///server.crt")
                            child.expect('#')
                            break
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            child.sendline("nxapi certificate enable")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to enable certificate "+\
                    "in device using nxapi certificate enable command")
            child.expect([pexpect.EOF, pexpect.TIMEOUT])
            self.log_mul_dev += 1
        self.cp_keypem = "cp ./Utilities/TlsCerts/server.key "+\
            "./Utilities/TlsCerts/xnc-privatekey.pem"
        try:
            self.cp_keypem_res = call(str(self.cp_keypem), \
                                shell=True)
            if self.cp_keypem_res == 0:
                LOGGER.info("Copy server.key file to xnc-privatekey.pem "+\
                    "file success")
            else:
                LOGGER.error("Failed to Copy server.key file to "+\
                    "xnc-privatekey.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy server.key file to "+\
                "xnc-privatekey.pem file")
            sys.exit(0)
        self.cp_certpem = "cp ./Utilities/TlsCerts/server.crt "+\
                            "./Utilities/TlsCerts/xnc-cert.pem"
        try:
            self.cp_certpem_res = call(str(self.cp_certpem), \
                                  shell=True)
            if self.cp_certpem_res == 0:
                LOGGER.info("Copy server.crt file to xnc-cert.pem "+\
                    "file success")
            else:
                LOGGER.error("Failed to Copy server.crt file to "+\
                    "xnc-cert.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy server.crt file to "+\
                "xnc-cert.pem file")
            sys.exit(0)
        self.cp_xncpem = "cat ./Utilities/TlsCerts/xnc-privatekey.pem "+\
        "./Utilities/TlsCerts/xnc-cert.pem > ./Utilities/TlsCerts/xnc.pem"
        try:
            self.cp_xncpem_res = call(str(self.cp_xncpem), \
                                 shell=True)
            if self.cp_xncpem_res == 0:
                LOGGER.info("Copy xnc-privatekey.pem and xnc-cert.pem "+\
                    "file to xnc.pem file success")
            else:
                LOGGER.error("Failed to Copy xnc-privatekey.pem and "+\
                    "xnc-cert.pem file to xnc.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy xnc-privatekey.pem and "+\
                    "xnc-cert.pem file to xnc.pem file")
            sys.exit(0)
        self.pass_pro = "openssl pkcs12 -export -out "+\
         "./Utilities/TlsCerts/xnc.p12 "+\
         "-in ./Utilities/TlsCerts/xnc.pem -password pass:"+\
         self.keystore_password
        try:
            self.pass_pro_res = call(str(self.pass_pro), \
                                shell=True, \
                                stdout=PIPE, \
                                stderr=STDOUT)
            if self.pass_pro_res == 0:
                LOGGER.info("Generate xnc.p12 file success")
            else:
                LOGGER.error("Failed to Generate xnc.p12 file -step29")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate xnc.p12 file -step29")
            sys.exit(0)
        #pdb.set_trace()
        self.xncp_tlskey = "keytool -importkeystore -srckeystore "+\
        "./Utilities/TlsCerts/xnc.p12 -srcstoretype pkcs12 -destkeystore "+\
        "./Utilities/TlsCerts/tlsKeyStore -deststoretype jks -srcstorepass "+\
        self.keystore_password+" -deststorepass "+self.keystore_password
        try:
            self.xncp_tlskey_res = call(str(self.xncp_tlskey), \
                                   shell=True, \
                                   stdout=PIPE, \
                                   stderr=STDOUT)
            if self.xncp_tlskey_res == 0:
                LOGGER.info("Convert the xnc.p12 to a Java KeyStore "+\
                    "- tlsKeyStore file success")
            else:
                LOGGER.error("Failed to Convert the xnc.p12 to a Java "+\
                    "KeyStore (tlsKeyStore) file -step31")
                #sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Convert the xnc.p12 to a Java "+\
                    "KeyStore (tlsKeyStore) file -step31")
            #sys.exit(0)
        self.capem_sw = "cp ./Utilities/TlsCerts/mypersonalca/certs/ca.pem "+\
        "./Utilities/TlsCerts/sw-cacert.pem"
        try:
            self.capem_sw_res = call(str(self.capem_sw), shell=True)
            if self.capem_sw_res == 0:
                LOGGER.info("Copy ca.pem file to sw-cacert.pem file success")
            else:
                LOGGER.error("Failed to Copy xnc-privatekey.pem and "+\
                    "xnc-cert.pem file to xnc.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy xnc-privatekey.pem and "+\
                    "xnc-cert.pem file to xnc.pem file")
            sys.exit(0)
        self.sw_tlstrust = "keytool -import -alias swca1 -file "+\
        "./Utilities/TlsCerts/sw-cacert.pem -keystore ./Utilities/TlsCerts/tlsTrustStore "+\
        "-storepass "+self.keystore_password+" -noprompt"
        try:
            self.sw_tlstrust_res = call(str(self.sw_tlstrust), \
                                   shell=True, \
                                   stdout=PIPE, \
                                   stderr=STDOUT)
            if self.sw_tlstrust_res == 0:
                LOGGER.info("Convert the sw-cacert.pem file to a Java "+\
                    "TrustStore - tlsTrustStore file success")
            else:
                LOGGER.error("Failed to Convert the sw-cacert.pem to a "+\
                    "Java TrustStore - tlsTrustStore file -step34")
                #sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Convert the sw-cacert.pem to a "+\
                    "Java TrustStore - tlsTrustStore file -step34")
            #sys.exit(0)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.login_mulser = 0
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.tem_serpath = ""
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.load(file_ptr)
                self.xnc_pwd = str(confi['xnc_password'])
                self.xnc_usr = str(confi['xnc_username'])                
        except OSError:
            LOGGER.error("Failed to open input yaml file")
        while (self.login_mulser < len(self.server_ip_list)):
            self.tem_serip = self.server_ip_list[self.login_mulser]
            self.tem_seruser = self.server_user_list[self.login_mulser]
            self.temp_serpass = self.server_password_list[self.login_mulser]
            self.tem_serpath = self.server_path_list[self.login_mulser]
            self.tem_port = self.server_port_list[self.login_mulser]
            xnc_path = self.tem_serpath[:-14]
            #pdb.set_trace()
            if self.tem_port != 0:
                try:
                    ssh = paramiko.SSHClient()
                    server = self.tem_serip
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(server, port=self.tem_port, username=self.tem_seruser, password=self.temp_serpass)
                    sftp = ssh.open_sftp()
                    localpath = './Utilities/TlsCerts/tlsTrustStore'
                    remotepath = '/root/xnc/configuration/tlsTrustStore'
                    sftp.put(localpath, remotepath)
                    local = './Utilities/TlsCerts/tlsKeyStore'
                    remote = '/root/xnc/configuration/tlsKeyStore'
                    sftp.put(local, remote)
                    sftp.close()
                except paramiko.SSHException:
                    LOGGER.error("Error while ssh into the server")
                    sys.exit(0)
            else:
                try:
                    ssh = paramiko.SSHClient()
                    server = self.tem_serip
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(server, username=self.tem_seruser, password=self.temp_serpass)
                    sftp = ssh.open_sftp()
                    localpath = './Utilities/TlsCerts/tlsTrustStore'
                    remotepath = self.tem_serpath+'tlsTrustStore'
                    sftp.put(localpath, remotepath)
                    local = './Utilities/TlsCerts/tlsKeyStore'
                    remote = self.tem_serpath+'tlsKeyStore'
                    sftp.put(local, remote)
                    sftp.close()
                except paramiko.SSHException:
                    LOGGER.error("Error while ssh into the server")
                    exit(0)
            time.sleep(5)
            #pdb.set_trace()
            self.run_ndb = 'cd '+xnc_path+' ;./runxnc.sh -osgiPasswordSync '+\
            '-tls -tlskeystore ./configuration/tlsKeyStore -tlstruststore '+\
            './configuration/tlsTrustStore'
            self.run_n = str(self.run_ndb)
            if self.tem_port != 0:
                self.run_n += '\n'
                try:
                    chan = ssh.invoke_shell()
                    chan.send(self.run_n)
                except OSError:
                    LOGGER.error("Server "+self.tem_serip+" Failed Run NDB"+\
                        " in TLS mode")
                    sys.exit(0)
            else:
                try:
                    stdin, stdout, stderr = ssh.exec_command(self.run_n)
                    stdin.write(self.xnc_pwd+"\n")
                    #print stdout.readlines()
                    LOGGER.info("Server "+self.tem_serip+" Run NDB in TLS"+\
                        " mode success")
                except OSError:
                    LOGGER.error("Server "+self.tem_serip+" Failed Run NDB"+\
                        " in TLS mode")
                    sys.exit(0)
            time.sleep(75)
            flag = True
            timeout = time.time() + 60*5
            while(flag):
                if time.time() <= timeout:
                    if self.tem_port != 0:
                        try:
                            ssh = paramiko.SSHClient()
                            server = self.tem_serip
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect(server, port=self.tem_port, username=self.tem_seruser, password=self.temp_serpass)
                            sftp = ssh.open_sftp()
                            localpath = '/root/xnc/logs/xnc.log'
                            remotepath = './Utilities/TlsCerts/xnc.log'
                            #pdb.set_trace()
                            sftp.put(localpath, remotepath)
                            local = '/root/xnc/logs/xnc.log'
                            remote = './Utilities/TlsCerts/xnc.log'
                            sftp.put(local, remote)
                            sftp.close()
                        except:
                            LOGGER.error("Error while ssh into the server")
                            sys.exit(0)
                    else:
                        try:
                            #pdb.set_trace()
                            ssh = paramiko.SSHClient()
                            server = self.tem_serip
                            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                            ssh.connect(server, username=self.tem_seruser, password=self.temp_serpass)
                            sftp = ssh.open_sftp()
                            localpath = xnc_path+'logs/xnc.log'
                            remotepath = './Utilities/TlsCerts/xnc.log'
                            sftp.get(localpath, remotepath)
                            local = xnc_path+'logs/xnc.log'
                            remote = './Utilities/TlsCerts/xnc.log'
                            sftp.get(local, remote)
                            sftp.close()
                        except:
                            LOGGER.error("Error while ssh into the server11")
                            exit(0)
                    try:
                        with open("./Utilities/TlsCerts/xnc.log", 'r') as fil_ptr:
                            for line in fil_ptr:
                                if 'Started \'Cisco Extensible Network Controller (XNC)\' version' in line:
                                    flag = False
                                    break
                                else:
                                    flag = True
                        continue
                    except OSError:
                        LOGGER.error("Failed to open xnc log file")
                        sys.exit(0)
                else:
                    LOGGER.error("Failed to start NDB in TLS mode")
                    sys.exit(0)
            time.sleep(15)
            #pdb.set_trace()
            self.prov_pass = 'cd '+xnc_path+'bin/ ;./xnc '+\
                'config-keystore-passwords --user '+self.xnc_usr+\
                ' --password '+self.xnc_pwd+' --url https://'+self.tem_serip+\
                ':8443 --verbose --keystore-password '+self.keystore_password+\
                ' --truststore-password '+self.keystore_password
            self.prov_pass_b = str(self.prov_pass)
            if self.tem_port == 0:
                try:
                    stdin, stdout, stderr = ssh.exec_command(self.prov_pass_b)
                    LOGGER.info("Server "+self.tem_serip+" Run command of "+\
                        "provided TLSKeyStore and TrustStore success")
                except OSError:
                    LOGGER.error("Server "+self.tem_serip+" Failed to Run "+\
                        "command of provided TLSKeyStore and TrustStore")
                    sys.exit(0)
            else:
                self.prov_pass_b += '\n'
                try:
                    chan = ssh.invoke_shell()
                    chan.send(self.prov_pass_b)
                except OSError:
                    LOGGER.error("Server "+self.tem_serip+" Failed to Run "+\
                        "command of provided TLSKeyStore and TrustStore")
                    sys.exit(0)
            time.sleep(10)
            self.login_mulser += 1
            ssh.close()

if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    #sys.stdout = os.devnull
    if not os.path.isdir('./Utilities/Log'):
        os.mkdir("./Utilities/Log")
    #sys.stdout = open(os.devnull, "w")
    if '--quiet' in sys.argv:
        FILENAME = os.path.join(DIR, './Utilities/Log/Logfile.log')            
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        FILE_LOG_HANDLER = logging.FileHandler(FILENAME)
        FILE_LOG_HANDLER.setLevel(logging.DEBUG)
        FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')        
        FILE_LOG_HANDLER.setFormatter(FORMATTER)
        LOGGER.addHandler(FILE_LOG_HANDLER)
    else:
        FILENAME = os.path.join(DIR, './Utilities/Log/Logfile.log')            
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        CON_LOG_HANDLER = logging.StreamHandler()
        FILE_LOG_HANDLER = logging.FileHandler(FILENAME)
        FILE_LOG_HANDLER.setLevel(logging.DEBUG)
        CON_LOG_HANDLER.setLevel(logging.DEBUG)
        FORMATTER = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        FILE_LOG_HANDLER.setFormatter(FORMATTER)
        CON_LOG_HANDLER.setFormatter(FORMATTER)
        LOGGER.addHandler(FILE_LOG_HANDLER)
        LOGGER.addHandler(CON_LOG_HANDLER)    
    INPUTFILE = os.path.join(DIR, './Utilities/Input/inputfile.yaml')
    D1 = Device()
    D1.method_one()
    D1.method_two()


