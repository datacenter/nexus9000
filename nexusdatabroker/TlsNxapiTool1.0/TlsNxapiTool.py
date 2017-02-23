import os
import sys
import yaml
import requests
import json
import pdb
import subprocess
import logging
"""
nf = open(os.devnull, 'w')
sys.stdout = nf

child.logfile = open("temp.log", "w+")
nf = open(os.devnull, 'w')
sys.stdout = nf
"""
class Server(object):
    def __init__(self):
        self.conn_type = "https"
        with open('Utilities/Input/inputfile.yaml') as file_ptr:
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
            auth = {'username' : self.username, 'password' : self.password}
            response = requests.post(self.ndb_login_url, auth, verify=False)
            if response.status_code == 200:
            	
                logger.info("NDB server : %s login success."%(self.server_ip))
                assert 1 == 1
            else:
                logger.error("NDB server-%s login failed."%(self.server_ip))
                logger.info("NDB server : %s login failed."%(self.server_ip))
                assert 1 == 0
            return response.cookies
        except Exception as e:
            logger.error("%s"%(e))
            sys.exit()


class Device(Server):
    def __init__(self):
        self.conn_type = "https"
        with open('Utilities/Input/inputfile.yaml') as fil_ptr:
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
                self.device_response = requests.put(self.device_url,\
                 data=json.dumps(self.device_info), cookies=self.cookie,\
                 headers=self.headers, verify=False)
                
                logger.info("NDB server :  login success.device added")
        except Exception as exp_e:
            logger.error("%s"%(e))
if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    subprocess.call(" python tls_python_script.py 1", shell=True)
    subprocess.call(" python openssl.py 1", shell=True)
    if not os.path.isdir('Utilities/Log'):
        os.mkdir("Utilities/Log")

    filename = os.path.join(dir, 'Utilities/Log/Logfile.log')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    con_log_handler = logging.StreamHandler()
    file_log_handler = logging.FileHandler(filename)
    file_log_handler.setLevel(logging.DEBUG)
    con_log_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_log_handler.setFormatter(formatter)
    con_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)
    logger.addHandler(con_log_handler)
    DEV_ONE = Device()
    inputFile = os.path.join(dir, 'Utilities/Input/inputfile.yaml')
    
    with open(inputFile) as f:
        DEVICE_INFO = yaml.safe_load(f)
    for dic in DEVICE_INFO['IP'].keys():
        DEV_ONE.device(DEVICE_INFO['IP'][dic], "create")
