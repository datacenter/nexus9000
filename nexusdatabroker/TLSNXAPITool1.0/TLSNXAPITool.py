import os
import sys
import yaml
import requests
import json
import subprocess
import logging
import paramiko
# pylint: disable-msg=E0611
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

class Server(object):
    def __init__(self):
        self.conn_type = "https"
        with open(INPUTFILE) as file_ptr:
            confi = yaml.safe_load(file_ptr)
        self.server_ip = confi['ServerIP']['ServerIP1']['ip']
        self.username = confi['ServerIP']['ServerIP1']['user']
        self.password = confi['ServerIP']['ServerIP1']['password']
        self.port = '8443'
        self.ndb_login_url = ""
        self.headers = {
                     'Content-Type' : 'application/json',
                     'Authorization': 'Basic YWRtaW46YWRtaW4='
                     }
    def ndb_servrer_login(self):
        try:
            self.ndb_login_url = self.conn_type+"://"+self.server_ip+":"\
            +self.port+"/monitor/"
            #auth = {'username' : self.username, 'password' : self.password}
            auth = {'username' : 'admin', 'password' : 'admin'}
            proxies = {
  		"http": None,
  		"https": None,
	    }
            response = requests.post(url=self.ndb_login_url, \
                data=auth, proxies=proxies, verify=False)
            if response.status_code == 200:
                LOGGER.info("Server - "+self.server_ip+" NDB server "+\
                    "login success")
            else:
                LOGGER.error("Server - "+self.server_ip+"NDB server "+\
                    "login failed")
            return response.cookies
        except paramiko.SSHException:
            LOGGER.error("Server - "+self.server_ip+"NDB server "+\
                    "login failed")
            sys.exit(0)
class Device(Server):
    def __init__(self):
        self.conn_type = "https"
        with open(INPUTFILE) as fil_ptr:
            confi = yaml.safe_load(fil_ptr)
        self.server_ip = confi['ServerIP']['ServerIP1']['ip']
        self.port = '8443'
        self.cookie = None
        self.ndb_login_url = ""
        server = Server()
        self.device_url = ""
        self.device_response = 0
        self.cookie = server.ndb_servrer_login()
        self.headers = {
                     'Content-Type' : 'application/json',
                     'Authorization': 'Basic YWRtaW46YWRtaW4='
                      }
    def device(self, device_info, operation):
        try:
            self.device_info = device_info
            if operation == 'create':
                self.device_url = self.conn_type+"://"+\
                str(self.server_ip)+":"+str(self.port)+\
                "/controller/nb/v2/resourcemanager/node/"+\
                str(self.device_info['address'])
                proxies = {
 		    "http": None,
  		    "https": None,		}
                if self.device_info['port'] == int(443):
                    self.device_response = requests.put(url=self.device_url,\
                     data=json.dumps(self.device_info), cookies=self.cookie,\
                     headers=self.headers, proxies=proxies, verify=False)
                    #pylint: disable=maybe-no-member
                    if self.device_response.status_code == int(200):
                        LOGGER.info("Device - "+self.device_info['address']+\
                            " Device added successfully")
                    else:
                        LOGGER.error("Device - "+self.device_info['address']+\
                            " Failed to add device in NDB")
                else:
                    LOGGER.error("Device - "+self.device_info['address']+\
                        " Please specify port number 443 for device "+\
                        "to be added in TLS mode ")
        except paramiko.SSHException:
            LOGGER.error("Device - "+self.device_info['address']+\
                        " Failed to add device in NDB")
if __name__ == "__main__":
    FILE1 = '/etc/ssh/ssh_config'
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
    if len(sys.argv) == 2:
        if '--quiet' in sys.argv:
            pass
        else:
            LOGGER.error("Please provide valid arguments. Run"+\
                " python script along with --quiet argument")
            sys.exit(0)
    else:
        LOGGER.error("Run python script along with --quiet argument")
        sys.exit(0)
    subprocess.call(" python TLSScript.py 1", shell=True)
    subprocess.call(" python OpenSSL.py 1", shell=True)
    INPUTFILE = os.path.join(DIR, './Utilities/Input/inputfile.yaml')
    DEV_ONE = Device()
    with open(INPUTFILE) as f:
        DEVICE_INFO = yaml.safe_load(f)
    for dic in sorted(DEVICE_INFO['IP'].keys()):
        DEV_ONE.device(DEVICE_INFO['IP'][dic], "create")
