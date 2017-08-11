import os
import sys
import yaml
import requests
import subprocess
import logging
import paramiko
# pylint: disable-msg=E0611
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

class Server:
    def __init__(self):
        self.conn_type = "https"
        with open(INPUTFILE) as file_ptr:
            confi = yaml.safe_load(file_ptr)
        self.server_ip = confi['ServerIP']['ServerIP1']['ip']
        self.username = confi['ServerIP']['ServerIP1']['user']
        self.password = confi['ServerIP']['ServerIP1']['password']
        self.port = '8443'
        self.web_url = ""
        self.login_url = ""
        self.add_device_url = ""
        self.device_response = 0
        self.xnc_pwd = str(confi['xnc_password'])
        self.xnc_usr = str(confi['xnc_username'])
    def ndb_servrer_login(self):
        try:
            self.web_url = self.conn_type+"://"+self.server_ip+":"\
            +self.port+"/monitor/"
            self.login_url = self.conn_type+"://"+self.server_ip+":"\
            +self.port+"/monitor/j_security_check"
            login_payload = {"j_username" : self.xnc_usr, "j_password" : self.xnc_pwd}
            with open(INPUTFILE) as file_ptr:
                dev_info = yaml.safe_load(file_ptr)
            for dic in sorted(dev_info['IP'].keys()):
                add_device_payload = dev_info['IP'][dic]
                add_device_payload['connectiontype'] = 'NXAPI'
                add_device_payload['auxnode'] = 'false'
                for key in add_device_payload:
                    add_device_payload[key] = str(add_device_payload[key])
            self.add_device_url = str(self.conn_type+"://"+\
            str(self.server_ip)+":"+str(self.port)+\
            "/controller/web/devices/extended//element/add")
            #pylint: disable=maybe-no-member
            with requests.session() as ses:
                ses.get(self.web_url, verify=False)
                ses.post(self.login_url, data=login_payload, verify=False)
                ses.post(self.add_device_url, data=add_device_payload, verify=False)
                LOGGER.info("Device - "+add_device_payload['address']+\
                    " Device added successfully")
        except paramiko.SSHException:
            LOGGER.error("Device - "+add_device_payload['address']+\
                        " Failed to add device in NDB")
if __name__ == "__main__":
    FILE1 = '/etc/ssh/ssh_config'
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
    if '--quiet' in sys.argv:
        subprocess.call(" python TLSScript.py --quiet", shell=True)
        subprocess.call(" python OpenSSL.py --quiet", shell=True)
    else:
        subprocess.call(" python TLSScript.py 1", shell=True)
        subprocess.call(" python OpenSSL.py 1", shell=True)
    INPUTFILE = os.path.join(DIR, './Utilities/Input/inputfile.yaml')
    DEV = Server()
    DEV.ndb_servrer_login()
    os.system("rm -rf ./Utilities/TlsCerts/temp")
    os.system("rm -rf ./Utilities/TlsCerts/xnc.log")
