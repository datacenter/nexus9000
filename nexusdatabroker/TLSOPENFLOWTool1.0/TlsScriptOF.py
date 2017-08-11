import os
import subprocess
from subprocess import call, PIPE, STDOUT
import yaml
import sys
import time
import fileinput
import pexpect
import paramiko
import logging

class Reachable:
    def __init__(self):
        self.device_ip_list = []
        self.device_user_list = []
        self.device_password_list = []
        self.log_mul_dev = 0
        self.temp_ip = ""
        self.temp_user = ""
        self.temp_pass = ""
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
    def reachable_check(self):
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
            self.all_ips_from_yaml = sorted(confi['IP'].keys())
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        self.log_mul_dev = 0
        for val in self.all_ips_from_yaml:
            self.device_ip_list.append(confi['IP'][val]['address'])
            self.device_user_list.append(confi['IP'][val]['username'])
            self.device_password_list.append(confi['IP'][val]['password'])
        while(self.log_mul_dev < len(self.device_ip_list)):
            self.temp_ip = self.device_ip_list[self.log_mul_dev]
            self.temp_user = self.device_user_list[self.log_mul_dev]
            self.temp_pass = self.device_password_list[self.log_mul_dev]
            child = pexpect.spawn('telnet '+ self.temp_ip)
            time.sleep(3)
            try:
                child.expect('login: ')
            except:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - telnet: Unable to connect to remote host: "+\
                    "Connection refused")
                sys.exit(0)
            child.sendline(self.temp_user)
            time.sleep(3)
            try:
                child.expect('assword: ')
            except:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Login incorrect Provided User name is not correct")
                sys.exit(0)
            child.sendline(self.temp_pass)
            time.sleep(3)
            try:
                child.expect("#")
                LOGGER.info("Device "+str(self.temp_ip)+\
                    " Login success")
            except:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Login incorrect Provided Password is not correct")
                sys.exit(0)
            self.log_mul_dev += 1
        self.login_mulser = 0
        server_list = sorted(confi['ServerIP'].keys())
        for value in server_list:
            self.server_ip_list.append(confi['ServerIP']\
                    [value]['ip'])
            self.server_user_list.append(confi['ServerIP']\
                    [value]['user'])
            self.server_password_list.append(confi['ServerIP']\
                    [value]['password'])
        while (self.login_mulser < len(self.server_ip_list)):
            self.tem_serip = self.server_ip_list[self.login_mulser]
            self.tem_seruser = self.server_user_list[self.login_mulser]
            self.temp_serpass = self.server_password_list[self.login_mulser]
            try:
                ssh = paramiko.SSHClient()
                server = self.tem_serip
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(server, username=self.tem_seruser, password=self.temp_serpass)
            except:
                LOGGER.error("Server "+self.tem_serip+" Unable to connect to Server ")
                exit(0)
            try:
                stdin, stdout, stderr = ssh.exec_command("pwd")
                LOGGER.info("Server "+self.tem_serip+" Login Success ")
                #print stdout.read()
            except:
                LOGGER.error("Server "+self.tem_serip+" Failed Run NDB"+\
                    " in TLS mode")
                sys.exit(0)
            self.login_mulser += 1
            ssh.close()

class Openflow:
    def __init__(self):
        self.default_days_c = ""
        self.default_days = ""
        self.default_md_list = []
        self.default_md_c = ""
        self.default_md = ""
        self.default_bits_list = []
        self.default_bits_c = ""
        self.default_bits = ""
        self.commonname_list = ""
        self.commonname_c = ""
        self.common_name = ""
        self.organizationname_list = ""
        self.organization_name_c = ""
        self.organization_name = ""
        self.localityname_list = ""
        self.localityname_c = ""
        self.locality_name = ""
        self.state_name_list = ""
        self.state_name_c = ""
        self.state_name = ""
        self.country_name_list = ""
        self.country_name_c = ""
        self.countryname = ""
        self.emailaddress_list = ""
        self.emailaddress_c = ""
        self.email_address = ""
        self.organizationalunit_name_list = ""
        self.organizationalunit_name_c = ""
        self.organizational_unit_name = ""
        self.keystore_password = ""
        self.gen_key_ca = ""
        self.default_days_str = ""
        self.default_bits_str = ""
        self.gen_key_ca_files_result = ""
        self.cert_req = ""
        self.cert_req_result = ""
        self.cert_pem = ""
        self.cert_pem_result = ""
        self.device_ip_list = []
        self.device_user_list = []
        self.device_password_list = []
        self.log_mul_dev = 0
        self.temp_ip = ""
        self.temp_user = ""
        self.temp_pass = ""
        self.trustpoint_list = []
        self.trustpoint_val = ""
        self.trust_keyval = ""
        self.crypto = ""
        self.crypto1 = ""
        self.crypto2 = ""
        self.crypto3 = ""
        self.append_forwkey = 0
        self.app_forwkey_e = 0
        self.capem_sw_res = ""
        self.cp_keypem = ""
        self.cp_certpem = ""
        self.sw_tlstrust_res = ""
        self.cp_xncpem_res = ""
        self.sw_tlstrust = ""
        self.capem_sw = ""
        self.xncp_tlskey = ""
        self.pass_pro = ""
        self.pass_pro_res = ""
        self.copy_file = 1
        self.cp_certpem_res = ""
        self.xncp_tlskey_res = ""
        self.cp_keypem_res = ""
        self.cp_xncpem = ""
        self.server_path = ""
        self.cp_ser_speloc = ""
        self.prov_pass_b = ""
        self.cp_cert_speloc = ""
        self.copy_keystore_res = ""
        self.cp_trust_res = ""
        self.cp_trust = ""
        self.copy_keystore = ""
        self.run_n = ""
        self.run_ndb = ""
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.tem_serpath = ""
        self.prov_pass = ""
        self.cp_cert_speloc_res = ""
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
        self.server_path_list = []
        self.add_contr = ""
        self.trustpoint = ""
        self.all_ips_from_yaml = []
        self.domain_name = ""
        self.conf_domain = ""
        self.add_pipeline = ""
        self.cat_pem_out = ""
        self.pipeline_of_dev = ""
        self.tlscer_auth_sw = ""
        self.cryptokey = ""
        self.gen_crpyt_key = ""
        self.login_mulser = 0
        self.install_key = ""
        self.gen_trustpoint = ""
        self.cp_ser_speloc_res = ""
    def method_one(self):
        try:
            if os.path.exists("./Utilities/TlsCerts"):
                os.system("rm -rf ./Utilities/TlsCerts")
                os.mkdir("./Utilities/TlsCerts")
                LOGGER.info("TlsCerts Folder created successfully")
            else:
                os.mkdir("./Utilities/TlsCerts")
                LOGGER.info("TlsCerts Folder created successfully")
        except OSError:
            LOGGER.error("Failed to Create TlsCerts Folder")
        try:
            os.mkdir('./Utilities/TlsCerts/mypersonalca/')
            LOGGER.info("mypersonalca Folder created successfully "+\
            "under TlsCerts")
        except OSError:
            LOGGER.error("Failed to Create mypersonalca Folder "+\
            "under TlsCerts")
        try:
            os.mkdir('./Utilities/TlsCerts/mypersonalca/certs')
            LOGGER.info("certs Folder created successfully under "+\
            "TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create certs Folder under "+\
            "TlsCerts/mypersonalca")
        try:
            os.mkdir('./Utilities/TlsCerts/mypersonalca/private')
            LOGGER.info("private Folder created successfully "+\
        "under TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create private Folder "+\
        "under TlsCerts/mypersonalca")
        try:
            os.mkdir('./Utilities/TlsCerts/mypersonalca/crl')
            LOGGER.info("crl Folder created successfully under "+\
        "TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create crl Folder under "+\
        "TlsCerts/mypersonalca")
        try:
            os.mkdir('./Utilities/TlsCerts/temp/')
            LOGGER.info("temp Folder created successfully "+\
            "under TlsCerts")
        except OSError:
            LOGGER.error("Failed to Create temp Folder "+\
            "under TlsCerts")
        try:
            serial = open("./Utilities/TlsCerts/mypersonalca/"+\
        "serial", "w+")
            LOGGER.info("serial file created successfully under "+\
        "TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create serial file under "+\
        "TlsCerts/mypersonalca")
        try:
            serial.write("01\n")
            LOGGER.info("Write to serial file success")
        except OSError:
            LOGGER.error("Failed to write to serial file")
        try:
            indexfile = open('./Utilities/TlsCerts/mypersonalca/'+\
        'index.txt', 'w+')
            LOGGER.info("index text file created successfully "+\
        "under TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create index text file under "+\
        "TlsCerts/mypersonalca")
        conf_file_input = """
[ ca ]
default_ca = mypersonalca
[ mypersonalca ]
dir = ./Utilities/TlsCerts/mypersonalca
certs = $dir/certs
crl_dir = $dir/crl
database = $dir/index.txt
new_certs_dir = $dir/certs
certificate = $dir/certs/ca.pem
serial = $dir/serial
crl = $dir/crl/crl.pem
private_key = $dir/private/ca.key
RANDFILE = $dir/private/.rand
x509_extensions = usr_cert
default_days = 365
default_crl_days= 30
default_md = sha1
preserve = no
policy = mypolicy
x509_extensions = certificate_extensions
[ mypolicy ]
commonName = optional
stateOrProvinceName = optional
countryName = optional
emailAddress = optional
organizationName = optional
organizationalUnitName = optional
[ certificate_extensions ]
basicConstraints = CA:false
[ req ]
default_keyfile = ./Utilities/TlsCerts/mypersonalca/private/ca.key
default_md = sha1
default_bits = 2048 
prompt = no
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
string_mask = utf8only
basicConstraints = CA:true
distinguished_name = root_ca_distinguished_name
x509_extensions = root_ca_extensions
[ root_ca_distinguished_name ]
countryName      = US
stateOrProvinceName     = Mass
localityName       = SanJose
organizationName       = Cisco
organizationalUnitName  = NDB
commonName             = www.cisco.com
emailAddress          = webmaster@cisco.com
[ root_ca_extensions ]
basicConstraints = CA:true
        """
        try:
            if not os.path.isfile("./Utilities/TlsCerts/ca.cnf"):
                tls_conf_file = open('./Utilities/TlsCerts/ca.cnf', 'w+')
            LOGGER.info("ca configuration file created successfully "+\
            "under TlsCerts/mypersonalca")
        except OSError:
            LOGGER.error("Failed to Create ca configuration file "+\
            "under TlsCerts/mypersonalca")
        try:
            tls_conf_file.write(conf_file_input)
            LOGGER.info("Write to ca configuration file success")
        except OSError:
            LOGGER.error("Failed to write to ca configuration file")
    def method_two(self):
        try:
            with open("./Utilities/TlsCerts/ca.cnf", 'r') as fil_ptr:
                for line in fil_ptr:
                    if 'default_days' in line:
                        self.default_days_c = line.split(" ")[-1]
                        self.default_days_c = self.default_days_c.strip()
                    if 'default_md' in line:
                        line1 = line.strip()
                        self.default_md_list = line1.split(" ")
                        self.default_md_c = self.default_md_list[2]
                    if 'default_bits' in line:
                        line2 = line.strip()
                        self.default_bits_list = line2.split(" ")
                        self.default_bits_c = self.default_bits_list[2]
                    if 'commonName' in line:
                        self.commonname_list = line.split(" ")[-1]
                        self.commonname_c = self.commonname_list.strip()
                    if 'organizationName' in line:
                        self.organizationname_list = line.split(" ")[-1]
                        self.organization_name_c = \
                        self.organizationname_list.strip()
                    if 'localityName' in line:
                        self.localityname_list = line.split(" ")[-1]
                        self.localityname_c = self.localityname_list.strip()
                    if 'stateOrProvinceName' in line:
                        self.state_name_list = line.split(" ")[-1]
                        self.state_name_c = \
                        self.state_name_list.strip()
                    if 'countryName' in line:
                        self.country_name_list = line.split(" ")[-1]
                        self.country_name_c = self.country_name_list.strip()
                    if 'emailAddress' in line:
                        self.emailaddress_list = line.split(" ")[-1]
                        self.emailaddress_c = self.emailaddress_list.strip()
                    if 'organizationalUnitName' in line:
                        self.organizationalunit_name_list = line.split(" ")[-1]
                        self.organizationalunit_name_c = \
                        self.organizationalunit_name_list.strip()
        except OSError:
            LOGGER.error("Failed to open ca configuration file")
            sys.exit(0)
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
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
                self.default_days_str = str(self.default_days)
                self.default_bits_str = str(self.default_bits)
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        def replace_method(file1, searchexp, replaceexp):
            for line in fileinput.input(file1, inplace=1):
                try:
                    if searchexp in line:
                        line = line.replace(searchexp, replaceexp)
                        LOGGER.info("Replace value - "+str(replaceexp)+\
                            " in ca config file is success")
                    try:
                        sys.stdout.write(line)
                        #LOGGER.info("Write to ca config file is success")
                    except OSError:
                        LOGGER.error("Failed to replace value "+\
                        +str(replaceexp)+" in ca config file")
                except OSError:
                    LOGGER.error("Failed to replace values in ca config file")
        replace_method("./Utilities/TlsCerts/ca.cnf", self.organization_name_c,\
        str(self.organization_name))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.state_name_c, \
        str(self.state_name))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.country_name_c, \
        str(self.countryname))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.emailaddress_c, \
        str(self.email_address))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.localityname_c, \
        str(self.locality_name))
        replace_method("./Utilities/TlsCerts/ca.cnf", \
        self.organizationalunit_name_c, str(self.organizational_unit_name))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.commonname_c, \
        str(self.common_name))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.default_days_c, \
        str(self.default_days))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.default_md_c, \
        str(self.default_md))
        replace_method("./Utilities/TlsCerts/ca.cnf", self.default_bits_c, \
        str(self.default_bits))
    def method_three(self):
        self.gen_key_ca = str("openssl req -x509 -nodes -days "+\
                              self.default_days_str+"0 -newkey rsa:"+\
                              self.default_bits_str+" -out ./Utilities"+\
                              "/TlsCerts/"+\
                              "mypersonalca/certs/ca.pem "+\
                              "-outform PEM -keyout ./Utilities/TlsCerts/"+\
                              "mypersonalca/private/ca.key -batch "+\
                              "-config ./Utilities/TlsCerts/ca.cnf")
        try:
            self.gen_key_ca_files_result = call(self.gen_key_ca, \
                                           shell=True, \
                                           stdout=PIPE, \
                                           stderr=STDOUT)
            if self.gen_key_ca_files_result == 0:
                LOGGER.info("Generate ca.pem and ca.key files success")
            else:
                LOGGER.error("Failed to Generate ca.pem and "+\
                "ca.key files -step4")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate ca.pem and ca.key files -step4")
            sys.exit(0)
        self.cert_req = str("openssl req -newkey rsa:"+\
        self.default_bits_str+" -keyout ./Utilities/TlsCerts/cert.key "+\
        "-keyform PEM -out ./Utilities/TlsCerts/cert.req -outform PEM "+\
        "-config ./Utilities/TlsCerts/ca.cnf -passout pass:"+\
        self.keystore_password+" -batch")
        try:
            self.cert_req_result = call(self.cert_req, \
                                    shell=True, stdout=PIPE, stderr=STDOUT)
            if self.cert_req_result == 0:
                LOGGER.info("Generate the cert.key cert.req files success")
            else:
                LOGGER.error("Failed to Generate the cert.key cert.req files "+\
                "- step5")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate the cert.key cert.req files "+\
                "- step5")
            sys.exit(0)
        self.cert_pem = str("openssl ca -batch -notext -in "+\
        "./Utilities/TlsCerts/cert.req -out ./Utilities/TlsCerts/cert.pem "+\
        "-config ./Utilities/TlsCerts/ca.cnf")
        try:
            self.cert_pem_result = call(self.cert_pem, \
                                    shell=True, stdout=PIPE, stderr=STDOUT)
            if self.cert_pem_result == 0:
                LOGGER.info("Generate the cert.pem file success")
            else:
                LOGGER.error("Failed to Generate the cert.key cert.req files "+\
                    "- step5")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate the cert.pem file "+\
                "- step6")
            sys.exit(0)
    def method_four(self):
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
            self.all_ips_from_yaml = sorted(confi['IP'].keys())
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        self.log_mul_dev = 0
        self.default_bits = str(confi['default_bits'])
        for val in self.all_ips_from_yaml:
            self.device_ip_list.append(confi['IP'][val]['address'])
            self.device_user_list.append(confi['IP'][val]['username'])
            self.device_password_list.append(confi['IP'][val]['password'])
        while(self.log_mul_dev < len(self.device_ip_list)):
            self.temp_ip = self.device_ip_list[self.log_mul_dev]
            self.temp_user = self.device_user_list[self.log_mul_dev]
            self.temp_pass = self.device_password_list[self.log_mul_dev]
            child = pexpect.spawn('telnet '+ self.temp_ip)
            time.sleep(3)
            try:
                child.expect('login: ')
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - telnet: Unable to connect to remote host: "+\
                    "Connection refused")
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
            try:
                child.logfile = open("./Utilities/TlsCerts/temp/temp1.log", "w")
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
                sys.exit(0)
            child.sendline("show crypto ca trustpoints")
            try:
                child.expect("#")
            except OSError:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to fetch show crypto ca trustpoints"+\
                    " cli output")
                sys.exit(0)
            child.sendline("show crypto key mypubkey rsa")
            try:
                child.expect("#")
            except OSError:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to fetch show crypto key mypubkey "+\
                    " rsa cli output")
                sys.exit(0)
            try:
                with open("./Utilities/TlsCerts/temp/temp1.log", \
                    'r') as fil_ptr:
                    for line in fil_ptr:
                        if 'trustpoint:' in line:
                            self.trustpoint_list = line.split(" ")[1:]
                            self.trustpoint_val = self.trustpoint_list[0]
                            self.trustpoint_val = \
                            self.trustpoint_val.replace(";", "")
                            self.trustpoint_val = self.trustpoint_val.strip()
                            self.trust_keyval = self.trustpoint_list[2]
                            self.trust_keyval = self.trust_keyval.strip()
                            child.sendline("configure terminal")
                            child.expect("#")
                            self.crypto = "crypto ca trustpoint "+\
                            self.trustpoint_val
                            child.sendline(self.crypto)
                            child.expect("#")
                            child.sendline("delete certificate force")
                            child.expect("#")
                            with open("./Utilities/TlsCerts/temp/temp1.log", \
                                'r') as fil_ptr1:
                                for line in fil_ptr1:
                                    try:
                                        if 'could not perform identity '+\
                                            'certificate deletion'  in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " - trustpoint "+\
                                                self.trustpoint_val+
                                                " - Fail to delete "+\
                                                "certificate using delete "+\
                                                "certificate force cli "+\
                                                "command ")
                                            sys.exit(0)
                                        elif 'Internal error during command '+\
                                            'execution' in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " - trustpoint "+\
                                                self.trustpoint_val+
                                                " - Fail to delete certifi"+\
                                                "cate using delete "+\
                                                "certificate force cli "+\
                                                "command")
                                            sys.exit(0)
                                        else:
                                            continue
                                    except pexpect.ExceptionPexpect:
                                        sys.exit(0)
                            child.sendline("delete ca-certificate")
                            child.expect("#")
                            with open("./Utilities/TlsCerts/temp/temp1.log", \
                                'r') as fil_ptr1:
                                for line in fil_ptr1:
                                    try:
                                        if 'could not perform CA certificate'+\
                                            '(s) deletion' in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " - trustpoint "+\
                                                self.trustpoint_val+
                                                " - Fail to delete "+\
                                                "certificate using delete "+\
                                                "ca-certificate "+\
                                                "cli command ")
                                            sys.exit(0)
                                        else:
                                            continue
                                    except pexpect.ExceptionPexpect:
                                        sys.exit(0)
                            self.crypto1 = "no rsakeypair "+self.trust_keyval
                            child.sendline(str(self.crypto1))
                            child.expect("#")
                            with open("./Utilities/TlsCerts/temp/temp1.log", \
                                'r') as fil_ptr1:
                                for line in fil_ptr1:
                                    try:
                                        if 'disassociating rsa key-pair '+\
                                            'not allowed when identity '+\
                                            'certificate exists'  in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " Fail to disassociate rsa "+\
                                                "keypair using no rsakeypair "+\
                                                self.trust_keyval+" cli "+\
                                                "command ")
                                            sys.exit(0)
                                        elif 'specified key-pair label is '+\
                                            'not the one associated to the '+\
                                            'trustpoint' in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " Fail to disassociate "+\
                                                "rsa keypair using no "+\
                                                "rsakeypair "+\
                                                self.trust_keyval+\
                                                " cli command ")
                                            sys.exit(0)
                                        else:
                                            continue
                                    except pexpect.ExceptionPexpect:
                                        sys.exit(0)
                            child.sendline("exit")
                            child.expect("#")
                            self.crypto2 = "no crypto ca trustpoint "\
                            +self.trustpoint_val
                            child.sendline(str(self.crypto2))
                            child.expect("#")
                            with open("./Utilities/TlsCerts/temp/temp1.log", \
                                'r') as fil_ptr1:
                                for line in fil_ptr1:
                                    try:
                                        if 'rsa key-pair associated to '+\
                                            'trustpoint; disassociate it '+\
                                            'first'  in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " Fail to remove trustpoint "+\
                                                "using no crypto ca "+\
                                                "trustpoint "+\
                                                +self.trustpoint_val+" cli "+\
                                                "command - rsa key-pair "+\
                                                "associated to trustpoint; "+\
                                                "disassociate it first")
                                            sys.exit(0)
                                        else:
                                            continue
                                    except pexpect.ExceptionPexpect:
                                        sys.exit(0)
                            self.crypto3 = "crypto key zeroize rsa "+\
                            self.trust_keyval
                            child.sendline(self.crypto3)
                            child.expect("#")
                            with open("./Utilities/TlsCerts/temp/temp1.log", \
                                'r') as fil_ptr1:
                                for line in fil_ptr1:
                                    try:
                                        if 'could not zeroize rsa key-pair'  in line:
                                            LOGGER.error("Device "+\
                                                str(self.temp_ip)+\
                                                " Fail to zeroize rsa "+\
                                                "key-pair using no crypto "+\
                                                "key zeroize rsa "+\
                                                self.trust_keyval+\
                                                " key pair already "+\
                                                "associated and/or "+\
                                                "certificate exists for "+\
                                                "the trust point "+\
                                                "could not zeroize rsa "+\
                                                "key-pair")
                                            sys.exit(0)
                                        else:
                                            continue
                                    except pexpect.ExceptionPexpect:
                                        sys.exit(0)
                            time.sleep(2)
                            break
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
                sys.exit(0)
            child.sendline("show crypto ca trustpoints")
            child.expect("#")
            child.sendline("show crypto key mypubkey rsa")
            child.expect("#")
            child.sendline("show crypto ca certificates")
            child.expect("#")
            child.sendline("configure terminal")
            child.expect("#")
            self.domain_name = confi['Domain_name']
            self.trustpoint = confi['Trustpoint']
            self.cryptokey = confi['Cryptography_key']
            self.conf_domain = "ip domain-name "+self.domain_name
            child.sendline(str(self.conf_domain))
            try:
                child.expect("#")
                LOGGER.info("Domain name configured success")
            except pexpect.ExceptionPexpect:
                sys.exit(0)
            self.gen_crpyt_key = "crypto key generate rsa label "+\
            self.cryptokey+" exportable modulus "+self.default_bits
            child.sendline(str(self.gen_crpyt_key))
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                sys.exit(0)
            try:
                with open("./Utilities/TlsCerts/temp/temp1.log", \
                    'r') as fil_ptr1:
                    for line in fil_ptr1:
                        try:
                            if '% Invalid number, range is'  in line:
                                LOGGER.error("Device "+\
                                    str(self.temp_ip)+\
                                    " Fail to generate rsa key-pair using "+\
                                    "crypto key generate rsa label "+\
                                    self.cryptokey+" exportable modulus "+\
                                    self.default_bits+" command Device "+\
                                    "won't support provided rsa "+\
                                    "default-bits "+self.default_bits)
                                sys.exit(0)
                            else:
                                continue
                        except pexpect.ExceptionPexpect:
                            sys.exit(0)
            except pexpect.ExceptionPexpect:
                sys.exit(0)
            self.gen_trustpoint = "crypto ca trustpoint "+self.trustpoint
            child.sendline(self.gen_trustpoint)
            child.expect("#")
            self.install_key = "rsakeypair "+self.cryptokey
            child.sendline(self.install_key)
            child.expect("#")
            child.sendline("exit")
            child.expect("#")
            LOGGER.info("Device "+str(self.temp_ip)+" Install "+\
                "trustpoint  -"+self.trustpoint+" and Install key -"+\
                self.cryptokey+" success")
            self.log_mul_dev += 1

class Openflow2:
    def __init__(self):
        self.keystore_password = ""
        self.gen_key_ca = ""
        self.default_days_str = ""
        self.default_bits_str = ""
        self.gen_key_ca_files_result = ""
        self.cert_req = ""
        self.cert_req_result = ""
        self.cert_pem = ""
        self.cert_pem_result = ""
        self.device_ip_list = []
        self.device_user_list = []
        self.device_password_list = []
        self.log_mul_dev = 0
        self.temp_ip = ""
        self.temp_user = ""
        self.temp_pass = ""
        self.trustpoint_list = []
        self.trustpoint_val = ""
        self.trust_keyval = ""
        self.crypto = ""
        self.crypto1 = ""
        self.crypto2 = ""
        self.crypto3 = ""
        self.append_forwkey = 0
        self.app_forwkey_e = 0
        self.capem_sw_res = ""
        self.cp_keypem = ""
        self.cp_certpem = ""
        self.sw_tlstrust_res = ""
        self.cp_xncpem_res = ""
        self.sw_tlstrust = ""
        self.capem_sw = ""
        self.xncp_tlskey = ""
        self.pass_pro = ""
        self.pass_pro_res = ""
        self.copy_file = 1
        self.cp_certpem_res = ""
        self.xncp_tlskey_res = ""
        self.cp_keypem_res = ""
        self.cp_xncpem = ""
        self.server_path = ""
        self.cp_ser_speloc = ""
        self.prov_pass_b = ""
        self.cp_cert_speloc = ""
        self.copy_keystore_res = ""
        self.cp_trust_res = ""
        self.cp_trust = ""
        self.copy_keystore = ""
        self.run_n = ""
        self.run_ndb = ""
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.tem_serpath = ""
        self.prov_pass = ""
        self.cp_cert_speloc_res = ""
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
        self.server_path_list = []
        self.add_contr = ""
        self.trustpoint = ""
        self.all_ips_from_yaml = []
        self.domain_name = ""
        self.conf_domain = ""
        self.add_pipeline = ""
        self.cat_pem_out = ""
        self.pipeline_of_dev = ""
        self.tlscer_auth_sw = ""
        self.cryptokey = ""
        self.gen_crpyt_key = ""
        self.login_mulser = 0
        self.install_key = ""
        self.gen_trustpoint = ""
        self.cp_ser_speloc_res = ""
        self.cat_pem_out1 = ""
        self.gen_newcert_pem = ""
        self.cat_pem_tem = ""
        self.copycer_to_dev = ""
        self.gen_cer_swi = ""
        self.server_port_list = []
        self.copycer_to_dev = ""
        self.tem_port = ""
        self.append_config = 0
        self.gen_newcert_pem_res = ""
    def method_five(self):
        try:
            self.cat_pem_out = subprocess.check_output("cat ./Utilities"+\
            "/TlsCerts/mypersonalca/certs/ca.pem ", shell=True)
            LOGGER.info("cat output of ca.pem file success")
        except OSError:
            LOGGER.error("Failed to get cat command output of ca.pem file"+\
                " - step 14")
            sys.exit(0)
        self.cat_pem_out = str(self.cat_pem_out)+"END OF INPUT:"
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
            self.all_ips_from_yaml = sorted(confi['IP'].keys())
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        self.log_mul_dev = 0
        for val in self.all_ips_from_yaml:
            self.device_ip_list.append(confi['IP'][val]['address'])
            self.device_user_list.append(confi['IP'][val]['username'])
            self.device_password_list.append(confi['IP'][val]['password'])
        self.trustpoint = confi['Trustpoint']
        self.cryptokey = confi['Cryptography_key']
        self.keystore_password = str(confi['keystore'])
        if not os.path.isfile("./Utilities/TlsCerts/temp/temptext.txt"):
            tls_conf_file = open('./Utilities/TlsCerts/temp/temptext.txt', \
                'w+')
        self.tempval = 10
        self.tempstr = ""            
        while(self.log_mul_dev < len(self.device_ip_list)):
            self.temp_ip = self.device_ip_list[self.log_mul_dev]
            self.temp_user = self.device_user_list[self.log_mul_dev]
            self.temp_pass = self.device_password_list[self.log_mul_dev]
            child = pexpect.spawn('telnet '+ self.temp_ip)
            time.sleep(3)
            try:
                child.expect('login: ')
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - telnet: Unable to connect to remote host: "+\
                    "Connection refused")
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
            try:
                child.logfile = open("./Utilities/TlsCerts/temp/temp2.log", "w")
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            child.sendline("configure terminal")
            try:
                child.expect("#")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " - Unable to configure in device using configuration "+\
                    "terminal command")
                sys.exit(0)
            time.sleep(20)
            self.copycer_to_dev = "crypto ca authenticate "+str(self.trustpoint)
            self.copycer_to_dev = str(self.copycer_to_dev)
            child.sendline(self.copycer_to_dev)
            time.sleep(20)
            try:
                child.expect("INPUT")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to authenticate trustpoint "+\
                    str(self.trustpoint)+" while expecting certificate"+\
                    " Device and server timings not matching")
                sys.exit(0)
            child.sendline(self.cat_pem_out)
            try:
                child.expect("accept this certificate")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to authenticate trustpoint "+\
                    str(self.trustpoint)+" while accepting certificate"+\
                    " Device and server timings not matching")
                sys.exit(0)
            child.sendline("yes")
            try:
                child.expect("#")
                LOGGER.info("Device "+str(self.temp_ip)+\
                    " Authentication of trustpoint "+str(self.trustpoint)+\
                    " success")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to authenticate trustpoint "+\
                    str(self.trustpoint)+" while verifying certificate"+\
                    " Device and server timings not matching")
                sys.exit(0)
            self.tempval += 1
            self.temp_path = ""
            self.temp_path = "./Utilities/TlsCerts/temp/temp"+str(self.tempval)+".log"
            self.temp_path = str(self.temp_path)
            try:
                child.logfile = open(self.temp_path, "w")
            except OSError:
                LOGGER.error("Failed to open temporary Log file")
            self.gen_cer_swi = "crypto ca enroll "+str(self.trustpoint)
            self.gen_cer_swi = str(self.gen_cer_swi)
            child.sendline(self.gen_cer_swi)
            try:
                child.expect("assword")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to enroll trustpoint "+\
                    str(self.trustpoint)+" in device step 16")
                sys.exit(0)
            child.sendline(self.keystore_password)
            try:
                child.expect("switch serial")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to enroll trustpoint "+\
                    str(self.trustpoint)+" in device step 16")
                sys.exit(0)
            child.sendline("no")
            try:
                child.expect("IP address")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to enroll trustpoint "+\
                    str(self.trustpoint)+" in device step 16")
                sys.exit(0)
            child.sendline("no")
            try:
                child.expect("Alternate Subject")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to enroll trustpoint "+\
                    str(self.trustpoint)+" in device step 16")
                sys.exit(0)
            child.sendline("no")
            try:
                child.expect("#")
                LOGGER.info("Device "+str(self.temp_ip)+\
                    " Enroll of trustpoint "+str(self.trustpoint)+\
                    " success")
            except pexpect.ExceptionPexpect:
                LOGGER.error("Device "+str(self.temp_ip)+\
                    " Failed to enroll trustpoint "+\
                    str(self.trustpoint)+" in device step 16")
                sys.exit(0)
            self.temp_cat = ""                
            try:
                self.temp_cat = str("cat "+self.temp_path)
                self.cat_pem_tem = subprocess.check_output(self.temp_cat, shell=True)
            except OSError:
                LOGGER.error("Failed to get cat command output from "+\
                    "temporary file - step 16")
                sys.exit(0)
            time.sleep(10)
            self.method_six()
            self.method_seven()
            self.method_eight()
            self.method_nine()
            self.log_mul_dev += 1
    def method_six(self):
        try:
            fil_ptr3 = open(self.temp_path)
        except OSError:
            LOGGER.error("Failed to open temporary Log file")
            sys.exit(0)
        self.temp_path2 = ""
        self.temp_path2 = "./Utilities/TlsCerts/temp/tempfile"+str(self.tempval)+".txt"
        self.temp_path2 = str(self.temp_path2)
        try:
            fil_ptr4 = open(self.temp_path2, 'a')
        except OSError:
            LOGGER.error("Failed to open temporary text file")
            sys.exit(0)
        copy_line = False
        for line in fil_ptr3.readlines():
            if 'Alternate Subject Name' in line:
                copy_line = True
            if copy_line:
                fil_ptr4.write(line)
        fil_ptr4.close()
        fil_ptr3.close()
        try:
            fil_ptr5 = open(self.temp_path2)
        except OSError:
            LOGGER.error("Failed to open temporary text file")
            sys.exit(0)
        self.temp_path4 = ""
        self.temp_path4 = "./Utilities/TlsCerts/temp/tempfile2"+str(self.tempval)+".txt"
        self.temp_path4 = str(self.temp_path4)            
        try:
            fil_ptr6 = open(self.temp_path4, 'a')
        except OSError:
            LOGGER.error("Failed to open temporary text file")
            sys.exit(0)
        copy_line1 = False
        for line in fil_ptr5.readlines():
            if '-----BEGIN CERTIFICATE REQUEST' in line:
                copy_line1 = True
            if copy_line1:
                fil_ptr6.write(line)
        fil_ptr5.close()
        fil_ptr6.close()
        try:
            data_file = open(self.temp_path4)
        except OSError:
            LOGGER.error("Failed to open temporary text file")
            sys.exit(0)
        begin_cert = ""
        end_cert = ""
        with open(self.temp_path4) as fi_p:
            for line in fi_p:
                if "BEGIN" in line:
                    begin_cert = line
                if "END" in line:
                    end_cert = line
        try:
            fil_ptr7 = open(self.temp_path4)
        except OSError:
            LOGGER.error("Failed to open temporary text file")
            sys.exit(0)
        block = ""
        btoe_cert = ""
        found1 = False
        for line in data_file:
            if found1:
                block += line
                if line.strip() == str(end_cert.strip()):
                    btoe_cert = block.strip()
                    break
            else:
                if line.strip() == str(begin_cert.strip()):
                    found1 = True
                    block = begin_cert
        fil_ptr7.close()
        self.temp_path5 = ""
        self.temp_path5 = "./Utilities/TlsCerts/n3k-cert"+str(self.tempval)+".req"
        self.temp_path5 = str(self.temp_path5)          
        try:
            if not os.path.isfile(self.temp_path5):
                tls_conf_file2 = open(self.temp_path5, "w+")
            LOGGER.info("n3k-cert.req file created successfully "+\
            "under TlsCerts")
        except OSError:
            LOGGER.error("Failed to Create n3k-cert.req file "+\
            "under TlsCerts")
            sys.exit(0)
        try:
            tls_conf_file2.write(btoe_cert)
            LOGGER.info("Write to n3k-cert.req file success")
        except OSError:
            LOGGER.error("Failed to write to n3k-cert.req file")
            sys.exit(0)
        time.sleep(3)  
    def method_seven(self):
        time.sleep(5)
        self.temp_path6 = ""
        self.temp_path6 = "./Utilities/TlsCerts/newcert"+str(self.tempval)+".pem"
        self.temp_path6 = str(self.temp_path6)            
        self.gen_newcert_pem = str("openssl ca -batch -in "+\
        self.temp_path5+\
         " -out "+self.temp_path6+\
         " -config ./Utilities/TlsCerts/ca.cnf")
        try:
            self.gen_newcert_pem_res = call(self.gen_newcert_pem, \
                                   shell=True, stdout=PIPE, stderr=STDOUT)
            if self.gen_newcert_pem_res == 0:
                LOGGER.info(" Generate newcert pem file success")
            else:
                LOGGER.error("Failed to generate newcert pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to generate newcert pem file")
            sys.exit(0)
        try:
            fil_ptr31 = open(self.temp_path6)
        except OSError:
            LOGGER.error("Failed to open newcert.pem file")
            sys.exit(0)
        self.temp_path7 = ""
        self.temp_path7 = "./Utilities/TlsCerts/temp/tempfile3"+str(self.tempval)+".log"
        self.temp_path7 = str(self.temp_path7)       
        try:
            fil_ptr32 = open(self.temp_path7, 'a')
        except OSError:
            LOGGER.error("Failed to open temporary Log file")
            sys.exit(0)
        copy_line2 = False
        for line in fil_ptr31.readlines():
            if 'BEGIN CERTIFICATE' in line:
                copy_line2 = True
            if copy_line2:
                fil_ptr32.write(line)
        fil_ptr31.close()
        fil_ptr32.close()
    def method_eight(self):
        try:
            self.var1 = str("cat "+self.temp_path7)
            self.cat_pem_out1 = subprocess.check_output(self.var1, shell=True)
        except OSError:
            LOGGER.error("Failed to get cat command output from "+\
                "temporary file - step 18")
            sys.exit(0)
    def method_nine(self):
        child = pexpect.spawn('telnet '+ self.temp_ip)
        time.sleep(3)
        try:
            child.expect('login: ')
        except pexpect.ExceptionPexpect:
            LOGGER.error("Device "+str(self.temp_ip)+\
                " - telnet: Unable to connect to remote host: "+\
                "Connection refused")
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
        self.temp_path8 = ""
        self.temp_path8 = "./Utilities/TlsCerts/temp/temp4"+str(self.tempval)+".log"
        self.temp_path8 = str(self.temp_path8)        
        try:
            child.logfile = open(self.temp_path8, "w")
        except OSError:
            LOGGER.error("Failed to open temporary Log file")
        child.sendline("configure terminal")
        try:
            child.expect("#")
        except pexpect.ExceptionPexpect:
            LOGGER.error("Device "+str(self.temp_ip)+\
                " - Unable to configure in device using configuration "+\
                "terminal command")
        time.sleep(10)
        self.copycer_to_dev = "crypto ca import "+str(self.trustpoint)+\
        " certificate"
        self.copycer_to_dev = str(self.copycer_to_dev)
        child.sendline(self.copycer_to_dev)
        try:
            child.expect("certificate in PEM format")
        except pexpect.ExceptionPexpect:
            LOGGER.error("Device "+str(self.temp_ip)+\
                " Failed to import trustpoint certificate"+\
                str(self.trustpoint))
            sys.exit(0)
        child.sendline(self.cat_pem_out1)
        try:
            child.expect("#")
            LOGGER.info("Device "+str(self.temp_ip)+\
                " Import of trustpoint certificate "+\
                str(self.trustpoint)+" success")
        except pexpect.ExceptionPexpect:
            LOGGER.error("Device "+str(self.temp_ip)+\
                " Failed to import trustpoint certificate"+\
                str(self.trustpoint))
            sys.exit(0)
    def method_ten(self):
        self.cp_keypem = "cp ./Utilities/TlsCerts/cert.key "+\
            "./Utilities/TlsCerts/xnc-privatekey.pem"
        try:
            self.cp_keypem_res = call(str(self.cp_keypem), \
                                shell=True)
            if self.cp_keypem_res == 0:
                LOGGER.info("Copy cert.key file to xnc-privatekey.pem "+\
                    "file success")
            else:
                LOGGER.error("Failed to Copy cert.key file to "+\
                    "xnc-privatekey.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy cert.key file to "+\
                    "xnc-privatekey.pem file")
            sys.exit(0)
        self.cp_certpem = "cp ./Utilities/TlsCerts/cert.pem "+\
        "./Utilities/TlsCerts/xnc-cert.pem"
        try:
            self.cp_certpem_res = call(str(self.cp_certpem), \
                                  shell=True)
            if self.cp_certpem_res == 0:
                LOGGER.info("Copy cert.pem file to xnc-cert.pem "+\
                    "file success")
            else:
                LOGGER.error("Failed to Copy cert.pem file to "+\
                    "xnc-cert.pem file")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Copy cert.pem file to "+\
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
         "-in ./Utilities/TlsCerts/xnc.pem -passin pass:"+\
         self.keystore_password+" -password pass:"+\
         self.keystore_password
        try:
            self.pass_pro_res = call(str(self.pass_pro), \
                                shell=True)
            if self.pass_pro_res == 0:
                LOGGER.info("Generate xnc.p12 file success")
            else:
                LOGGER.error("Failed to Generate xnc.p12 file -step29")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Generate xnc.p12 file -step29")
            sys.exit(0)
        self.xncp_tlskey = "keytool -importkeystore -srckeystore "+\
        "./Utilities/TlsCerts/xnc.p12 -srcstoretype pkcs12 -destkeystore "+\
        "./Utilities/TlsCerts/tlsKeyStore -deststoretype jks -srcstorepass "+\
        self.keystore_password+" -deststorepass "+self.keystore_password
        try:
            self.xncp_tlskey_res = call(str(self.xncp_tlskey), \
                                   shell=True, stdout=PIPE, stderr=STDOUT)
            if self.xncp_tlskey_res == 0:
                LOGGER.info("Convert the xnc.p12 to a Java KeyStore "+\
                    "- tlsKeyStore file success")
            else:
                LOGGER.error("Failed to Convert the xnc.p12 to a Java "+\
                    "KeyStore (tlsKeyStore) file -step31")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Convert the xnc.p12 to a Java "+\
                    "KeyStore (tlsKeyStore) file -step31")
            sys.exit(0)
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
        "./Utilities/TlsCerts/sw-cacert.pem -keystore ./Utilities/"+\
        "TlsCerts/tlsTrustStore "+\
        "-storepass "+self.keystore_password+" -noprompt"
        try:
            self.sw_tlstrust_res = call(str(self.sw_tlstrust), \
                shell=True, stdout=PIPE, stderr=STDOUT)
            if self.sw_tlstrust_res == 0:
                LOGGER.info("Convert the sw-cacert.pem file to a Java "+\
                    "TrustStore - tlsTrustStore file success")
            else:
                LOGGER.error("Failed to Convert the sw-cacert.pem to a "+\
                    "Java TrustStore - tlsTrustStore file -step34")
                sys.exit(0)
        except OSError:
            LOGGER.error("Failed to Convert the sw-cacert.pem to a "+\
                    "Java TrustStore - tlsTrustStore file -step34")
            sys.exit(0)
    def append_slash(self):
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
            self.all_ips_from_yaml = sorted(confi['IP'].keys())
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        self.server_path_list = []
        server_list = sorted(confi['ServerIP'].keys())
        for value in server_list:
            try:
                self.server_path_list.append(confi['ServerIP']\
                        [value]['path_ndb_build'])
            except OSError:
                LOGGER.error("Failed to append provided NDB path to list")
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
    def run_ndbser(self):
        try:
            with open(INPUTFILE, 'r') as file_ptr:
                confi = yaml.safe_load(file_ptr)
                self.xnc_pwd = str(confi['xnc_password'])
                self.xnc_usr = str(confi['xnc_username'])  
        except OSError:
            LOGGER.error("Failed to open input yaml file")
            sys.exit(0)
        self.login_mulser = 0
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.tem_serpath = ""
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
        self.server_port_list = []
        server_list = sorted(confi['ServerIP'].keys())
        for value in server_list:
            self.server_ip_list.append(confi['ServerIP']\
                    [value]['ip'])
            self.server_user_list.append(confi['ServerIP']\
                    [value]['user'])
            self.server_password_list.append(confi['ServerIP']\
                    [value]['password'])
            try:
                self.server_port_list.append(confi['ServerIP']\
                    [value]['port'])
            except KeyError:
                self.server_port_list.append(0)
        while (self.login_mulser < len(self.server_ip_list)):
            self.tem_serip = self.server_ip_list[self.login_mulser]
            self.tem_seruser = self.server_user_list[self.login_mulser]
            self.temp_serpass = self.server_password_list[self.login_mulser]
            self.tem_serpath = self.server_path_list[self.login_mulser]
            self.tem_port = self.server_port_list[self.login_mulser]
            xnc_path = self.tem_serpath[:-14]
            if self.copy_file == 1:
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
                    except OSError:
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
                    except OSError:
                        LOGGER.error("Error while ssh into the server")
                        exit(0)
            else:
                self.cp_ser_speloc = "cp -r ./Utilities/TlsCerts/server.key "+\
                self.tem_serpath
                self.cp_ser_speloc_res = call(str(self.cp_ser_speloc),\
                                                 shell=True)
                self.cp_cert_speloc = "cp -r ./Utilities/TlsCerts/server.crt "+\
                self.tem_serpath
                self.cp_cert_speloc_res = call(str(self.cp_cert_speloc)\
                                              , shell=True)
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
            timeout = time.time() + 60*3
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
                            sftp.put(localpath, remotepath)
                            local = '/root/xnc/logs/xnc.log'
                            remote = './Utilities/TlsCerts/xnc.log'
                            sftp.put(local, remote)
                            sftp.close()
                        except OSError:
                            LOGGER.error("Error while ssh into the server")
                            sys.exit(0)
                    else:
                        try:
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
                        except OSError:
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
            time.sleep(30)
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
    if len(sys.argv) == 1:
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
    elif len(sys.argv) == 2:
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
            LOGGER.error(" Run python script without arguments or along "+\
                "with --quiet argument")
            sys.exit(0)
    else:
        LOGGER.error(" Run python script without arguments or along "+\
                "with --quiet argument")
        sys.exit(0)
    INPUTFILE = os.path.join(DIR, './Utilities/Input/inputfile.yaml')
    D = Reachable()
    D.reachable_check()
    D1 = Openflow()
    D1.method_one()
    D1.method_two()
    D1.method_three()
    D1.method_four()
    D2 = Openflow2()
    D2.method_five()
    D2.method_ten()
    D2.append_slash()
    D2.run_ndbser()
