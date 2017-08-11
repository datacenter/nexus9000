import os
import time
import yaml
import pexpect
import sys
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
        self.login_mulser = 0
        self.all_ips_from_yaml = {}
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
                    " Device is not reachable")
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
                LOGGER.error("Server "+self.tem_serip+" Unable to "+\
                    "connect to Server ")
                exit(0)
            try:
                stdin, stdout, stderr = ssh.exec_command("pwd")
                LOGGER.info("Server "+self.tem_serip+" Login Success ")
            except:
                LOGGER.error("Server "+self.tem_serip+" Failed Run NDB"+\
                    " in TLS mode")
                sys.exit(0)
            self.login_mulser += 1
            ssh.close()
class Nxapi:
    def __init__(self):
        self.default_days_c = ""
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
        conf_file_input = """[ ca ]
default_ca              = CA_default
[ CA_default ]
dir                     = .
serial                  = $dir/serial
database                = $dir/index.txt
new_certs_dir           = $dir/newcerts
certs                   = $dir/certs
certificate             = $certs/cacert.pem
private_key             = $dir/private/cakey.pem
default_days            = 365
default_md              = sha256
preserve                = no
email_in_dn             = no
nameopt                 = default_ca
certopt                 = default_ca
policy                  = policy_match
copy_extensions         = copy
[ policy_match ]
countryName             = match
stateOrProvinceName     = match
organizationName        = match
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional
[ req ]
default_bits            = 2048                  # Size of keys
default_keyfile         = example.key           # name of generated keys
default_md              = sha256                  # message digest algorithm
string_mask             = nombstr               # permitted characters
distinguished_name      = req_distinguished_name
req_extensions          = v3_req
x509_extensions         = v3_req
[ req_distinguished_name ]
0.organizationName      = Organization Name (company)
organizationalUnitName  = Organizational Unit Name (department, division)
emailAddress            = Email Address
emailAddress_max        = 40
localityName            = Locality Name (city, district)
stateOrProvinceName     = State or Province Name (full name)
countryName             = Country Name (2 letter code)
countryName_min         = 2
countryName_max         = 2
commonName              = Common Name (hostname, IP, or your name)
commonName_max          = 64
# Default values for the above, for consistency and less typing.
commonName_default              = www.cisco.com
organizationName_default        = Cisco
localityName_default            = SanJose
stateOrProvinceName_default     = KAR
countryName_default             = US
emailAddress_default            = webmaster@cisco.com
organizationalUnitName_default  = NDB
[ v3_ca ]
basicConstraints        = CA:TRUE
subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always,issuer:always
[ v3_req ]
# Extensions to add to a certificate request
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName          = @alt_names
[alt_names]
IP.1   = 1.1.1.1
IP.2   = 2.2.2.2
IP.3   = 3.3.3.3
IP.4   = 4.4.4.4
IP.5   = 5.5.5.5
IP.6   = 6.6.6.6
IP.7   = 7.7.7.7
IP.8   = 8.8.8.8
IP.9   = 9.9.9.9
IP.10   = 10.10.10.10
[ server ]
basicConstraints=CA:FALSE
nsCertType                      = server
nsComment                       = "OpenSSL Generated Server Certificate"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer:always
[ client ]
basicConstraints=CA:FALSE
nsCertType                      = client
nsComment                       = "OpenSSL Generated Client Certificate"
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer:always"""
        try:
            if not os.path.isfile("./Utilities/TlsCerts/ca.conf"):
                tls_conf_file = open('./Utilities/TlsCerts/ca.conf', 'w+')
                LOGGER.info("CA configuration file created successfully "+\
                    "under TlsCerts")
        except OSError:
            LOGGER.error("Failed to Create CA configuration file "+\
                "under TlsCerts")
        try:
            tls_conf_file.write(conf_file_input)
            LOGGER.info("Write to CA configuration file success")
        except OSError:
            LOGGER.error("Failed to write to CA configuration file")

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
    D = Reachable()
    D.reachable_check()
    D1 = Nxapi()
    D1.method_one()
