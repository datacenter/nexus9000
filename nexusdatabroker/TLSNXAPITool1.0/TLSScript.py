import os
import logging

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
default_md              = sha1
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
default_md              = sha1                  # message digest algorithm
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
            if not os.path.isfile("./Utilities/TlsCerts/Example.conf"):
                tls_conf_file = open('./Utilities/TlsCerts/Example.conf', 'w+')
                LOGGER.info("Example configuration file created successfully "+\
                    "under TlsCerts")
        except OSError:
            LOGGER.error("Failed to Create Example configuration file "+\
                "under TlsCerts")
        try:
            tls_conf_file.write(conf_file_input)
            LOGGER.info("Write to Example configuration file success")
        except OSError:
            LOGGER.error("Failed to write to Example configuration file")

if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    if not os.path.isdir('./Utilities/Log'):
        os.mkdir("./Utilities/Log")
    FILENAME = os.path.join(DIR, './Utilities/Log/Logfile.log')
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    FILE_LOG_HANDLER = logging.FileHandler(FILENAME)
    FILE_LOG_HANDLER.setLevel(logging.DEBUG)
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    FILE_LOG_HANDLER.setFormatter(FORMATTER)
    LOGGER.addHandler(FILE_LOG_HANDLER)
    INPUTFILE = os.path.join(DIR, './Utilities/Input/inputfile.yaml')
    D1 = Nxapi()
    D1.method_one()
