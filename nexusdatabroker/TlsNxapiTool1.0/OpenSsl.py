from subprocess import call
import os 
import pdb
import time
import yaml
import pexpect
import sys
import fileinput
import paramiko



#take-input-from-config-filei
class Device:
    def __init__(self):
        self.ip_l = []
        self.cp_keypem_res = ""
        self.tem_serpath = ""
        self.cp_cert_speloc_res = ""
        self.prov_pass = ""
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

    def method_one(self):
        with open("Utilities/TlsCerts/Example.conf", 'r') as fil_ptr:
            for line in fil_ptr:
                if 'default_days' in line:
                    self.default_days_c = line.split(" ")[-1]
                    self.default_days_c = self.default_days_c.strip()
                if 'default_md' in line and 'digest' in line:
                    line1 = line.strip()
                    self.default_md_list = line1.split(" ")
                    self.default_md_list = filter(None, self.default_md_list)
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
        with open(filename, 'r') as file_ptr:
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
        def replace_method(file1, searchexp, replaceexp):
            for line in fileinput.input(file1, inplace=1):
                if searchexp in line:
                    line = line.replace(searchexp, replaceexp)
                sys.stdout.write(line)
        replace_method("Utilities/TlsCerts/Example.conf", self.organization_name_c,\
        str(self.organization_name))
        replace_method("Utilities/TlsCerts/Example.conf", self.state_name_c, \
        str(self.state_name))
        replace_method("Utilities/TlsCerts/Example.conf", self.country_name_c, \
        str(self.countryname))
        replace_method("Utilities/TlsCerts/Example.conf", self.emailaddress_c, \
        str(self.email_address))
        replace_method("Utilities/TlsCerts/Example.conf", self.localityname_c, \
        str(self.locality_name))
        replace_method("Utilities/TlsCerts/Example.conf", \
        self.organizationalunit_name_c, str(self.organization_name))
        replace_method("Utilities/TlsCerts/Example.conf", self.commonname_c, \
        str(self.common_name))
        self.all_ips_from_yaml = sorted(confi['IP'].keys())
        for val in self.all_ips_from_yaml:
            self.device_ip_list.append(confi['IP'][val]['address'])
            self.device_user_list.append(confi['IP'][val]['username'])
            self.device_password_list.append(confi['IP'][val]['password'])
        while self.replace_ip < len(self.device_ip_list):
            replace_method("Utilities/TlsCerts/Example.conf", \
                self.ip_l[self.replace_ip],\
                str(self.device_ip_list[self.replace_ip]))
            self.replace_ip += 1
        self.default_days_str = str(self.default_days)
        self.default_bits_str = str(self.default_bits)
    def method_two(self):
        with open(filename, 'r') as file_ptr:
            confi = yaml.load(file_ptr)
        self.gen_key_ca = str("openssl req -x509 -nodes -days "+\
                              self.default_days_str+"0 -newkey rsa:"+
                              self.default_bits_str+" -out Utilities/TlsCerts/"+\
                              "mypersonalca/certs/ca.pem \
                              -outform PEM -keyout Utilities/TlsCerts/"+\
                              "mypersonalca/private/ca.key -batch")
        self.gen_key_ca_files_result = call(self.gen_key_ca, \
                                           shell=True)
        self.gen_cert_key = str("openssl req -new -x509 -days "+\
                            self.default_days_str+" -nodes -out \
                            Utilities/TlsCerts/server.crt -keyout \
                            Utilities/TlsCerts/server.key -config \
                            Utilities/TlsCerts/Example.conf -batch")
        self.gen_cert_key_result = call(self.gen_cert_key, \
                                       shell=True)
        self.ip = confi['ServerIP']['ServerIP1']['ip']
        self.user = confi['ServerIP']['ServerIP1']['user']
        self.password = confi['ServerIP']['ServerIP1']['password']
        self.path = confi['ServerIP']['ServerIP1']['path_ndb_build']
        self.server_ip_list = []
        self.server_user_list = []
        self.server_password_list = []
        self.server_path_list = []
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
        self.append_forwkey = 0
        while self.append_forwkey < len(self.server_path_list):
            suffix = "/"
            self.server_path = str(self.server_path_list\
                              [self.append_forwkey])
            if self.server_path.endswith(suffix) == False:
                self.server_path = self.server_path+"/"
                self.server_path_list[self.append_forwkey] \
                    = str(self.server_path)
            self.append_forwkey += 1
        self.app_forwkey_e = 0
        while self.app_forwkey_e < len(self.server_path_list):
            suffix = "/"
            self.server_path = str(self.server_path_list\
                              [self.app_forwkey_e])
            if self.server_path.startswith(suffix) == False:
                self.server_path = "/"+self.server_path
                self.server_path_list[self.app_forwkey_e] = \
                   str(self.server_path)
            self.app_forwkey_e += 1
        self.append_config = 0
        while self.append_config < len(self.server_path_list):
            suffix = "configuration"+"/"
            self.server_path = str(self.server_path_list\
                              [self.append_config])
            if self.server_path.endswith(suffix) == False:
                self.server_path = self.server_path+"configuration"+"/"
                self.server_path_list[self.append_config] \
                    = str(self.server_path)
            self.append_config += 1
        self.ip = self.server_ip_list[0]
        self.user = self.server_user_list[0]
        self.password = self.server_password_list[0]
        self.path = self.server_path_list[0]
        if self.copy_file == 1:
            self.cp_key_lhser = "sshpass -p "+ self.password + \
                " scp -r ./Utilities/TlsCerts/server.key " + self.user +\
                '@'+self.ip +':'+self.path
            self.cp_key_lhser_res = call(str(self.cp_key_lhser), shell=True)
            self.cp_cert_lhser = "sshpass -p "+ self.password + \
                " scp -r ./Utilities/TlsCerts/server.crt " + self.user +\
                '@'+self.ip +':'+self.path
            self.cp_cert_lhser_res = call(str(self.cp_cert_lhser), shell=True)
        else:
            self.cp_ser_speloc = "cp -r ./Utilities/TlsCerts/server.key "+self.path
            self.cp_ser_speloc_res = call(str(self.cp_ser_speloc), shell=True)
            self.cp_cert_speloc = "cp -r ./Utilities/TlsCerts/server.crt "+self.path
            self.cp_cert_speloc_res = call(str(self.cp_cert_speloc), shell=True)
	
        while(self.log_mul_dev < len(self.device_ip_list)):
            self.temp_ip = self.device_ip_list[self.log_mul_dev]
            self.temp_user = self.device_user_list[self.log_mul_dev]
            self.temp_pass = self.device_password_list[self.log_mul_dev]
            child = pexpect.spawn('telnet '+ self.temp_ip)
            time.sleep(3)
            child.expect('login: ')
            child.sendline(self.temp_user)
            time.sleep(3)
            child.expect('assword: ')
            child.sendline(self.temp_pass)
            time.sleep(3)
            child.expect("#")
            child.logfile = open("temp.log", "w")
            child.sendline("dir bootflash:server.key")
            with open("temp.log", "r") as fp:
                for line in fp:
                    if "server.key" in line:
                        child.sendline("delete bootflash:server.key")
                        child.expect("[y]")
                        child.sendline("y")
                        break
            child.sendline("dir bootflash:server.crt")
            with open("temp.log", "r") as fp1:
                for line1 in fp1:
                    if "server.crt" in line1:
                        child.sendline("delete bootflash:server.crt")
                        child.expect("[y]")
                        child.sendline("y")
                        break
            self.copy_keyfile = str("copy scp://"+self.user+'@'+\
            	self.ip+self.path+"server.key "+
            	"bootflash:/// vrf management")
            child.sendline(self.copy_keyfile)
            try:
                child.expect ("continue")
                child.sendline ("yes")
                child.expect ('password: ')
                child.sendline (self.password)
                child.expect('#')
            except:
                child.expect ('password: ')
                child.sendline (self.password)
                child.expect('#')
            time.sleep(10)
            self.cp_certfile = str("copy scp://"+self.user+'@'+\
            	self.ip+self.path+"server.crt bootflash:/// vrf management")
            child.sendline(self.cp_certfile)
            try:
                child.expect ("continue")
                child.sendline ("yes")
                child.expect ('password: ')
                child.sendline (self.password)
                child.expect('#')
            except:
                child.expect ('password: ')
                child.sendline (self.password)
                child.expect('#')
            child.sendline("configure terminal")
            child.expect("#")
            child.sendline("nxapi certificate httpskey "+
            	"keyfile bootflash:///server.key")
            child.expect('#')
            time.sleep(5)
            with open("temp.log", "r") as fp4:
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
            child.sendline("nxapi certificate httpscrt"+ \
            	" certfile bootflash:///server.crt")
            child.expect('#')
            time.sleep(5)
            with open("temp.log", "r") as fp5:
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
            child.sendline("nxapi certificate enable")
            child.expect('#')
            child.sendline("configure terminal")
            child.expect("#")
            child.sendline("feature nxapi")
            child.expect("#")
            child.expect([pexpect.EOF, pexpect.TIMEOUT])
            self.log_mul_dev += 1
        self.cp_keypem = "cp Utilities/TlsCerts/server.key "+\
            "Utilities/TlsCerts/xnc-privatekey.pem"
        self.cp_keypem_res = call(str(self.cp_keypem), \
                                shell=True)
        self.cp_certpem = "cp Utilities/TlsCerts/server.crt Utilities/TlsCerts/xnc-cert.pem"
        self.cp_certpem_res = call(str(self.cp_certpem), \
                                  shell=True)
        self.cp_xncpem = "cat Utilities/TlsCerts/xnc-privatekey.pem "+\
        "Utilities/TlsCerts/xnc-cert.pem > Utilities/TlsCerts/xnc.pem"
        self.cp_xncpem_res = call(str(self.cp_xncpem), \
                                 shell=True)
        self.pass_pro = "openssl pkcs12 -export -out Utilities/TlsCerts/xnc.p12 "+\
         "-in Utilities/TlsCerts/xnc.pem -password pass:"+self.keystore_password
        self.pass_pro_res = call(str(self.pass_pro), \
                                shell=True)
        self.xncp_tlskey = "keytool -importkeystore -srckeystore "+\
        "Utilities/TlsCerts/xnc.p12 -srcstoretype pkcs12 -destkeystore "+\
        "Utilities/TlsCerts/tlsKeyStore -deststoretype jks -srcstorepass "+\
        self.keystore_password+" -deststorepass "+self.keystore_password
        self.xncp_tlskey_res = call(str(self.xncp_tlskey), \
                                   shell=True)
        self.capem_sw = "cp Utilities/TlsCerts/mypersonalca/certs/ca.pem "+\
        "Utilities/TlsCerts/sw-cacert.pem"
        self.capem_sw_res = call(str(self.capem_sw), shell=True)
        self.sw_tlstrust = "keytool -import -alias swca1 -file "+\
        "Utilities/TlsCerts/sw-cacert.pem -keystore Utilities/TlsCerts/tlsTrustStore "+\
        "-storepass "+self.keystore_password+" -noprompt"
        self.sw_tlstrust_res = call(str(self.sw_tlstrust), \
                                   shell=True)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.login_mulser = 0
        self.tem_serip = ""
        self.tem_seruser = ""
        self.temp_serpass = ""
        self.tem_serpath = ""
        
        while (self.login_mulser < len(self.server_ip_list)):
            self.tem_serip = self.server_ip_list[self.login_mulser]
            self.tem_seruser = self.server_user_list[self.login_mulser]
            self.temp_serpass = self.server_password_list[self.login_mulser]
            self.tem_serpath = self.server_path_list[self.login_mulser]
            xnc_path = self.tem_serpath[:-14]
            if self.copy_file == 1:
                self.cp_trust = "sshpass -p "+ self.temp_serpass +\
                " scp -r ./Utilities/TlsCerts/tlsTrustStore " + self.tem_seruser +\
                '@'+self.tem_serip+':'+self.tem_serpath
                self.cp_trust_res = call(str(self.cp_trust), shell=True)
                self.copy_keystore = "sshpass -p "+ self.temp_serpass+"\
                scp -r ./Utilities/TlsCerts/tlsKeyStore "+ self.tem_seruser +\
                '@'+self.tem_serip +':'+ self.tem_serpath
                self.copy_keystore_res = call(str(self.copy_keystore), \
                                                shell=True)
            else:
                self.cp_ser_speloc = "cp -r ./Utilities/TlsCerts/server.key "+\
                self.path
                self.cp_ser_speloc_res = call(str(self.cp_ser_speloc),\
                                                 shell=True)
                self.cp_cert_speloc = "cp -r ./Utilities/TlsCerts/server.crt "+\
                self.path
                self.cp_cert_speloc_res = call(str(self.cp_cert_speloc)\
                                              , shell=True)
            ssh.connect(self.tem_serip, username=self.tem_seruser, \
            	password=self.temp_serpass)
            if str(self.server_ip_list[0]) == str(self.tem_serip):
                del_cert_file = str("cd "+self.server_path_list[0] +\
                                        ";rm -rf server.crt")
                stdin, stdout, stderr = ssh.exec_command(del_cert_file)
                time.sleep(5)
                del_key_file = str("cd "+self.server_path_list[0] +\
                                   ";rm -rf server.key")
                stdin, stdout, stderr = ssh.exec_command(del_key_file)
            time.sleep(5)
            self.run_ndb = 'cd '+xnc_path+' ;./runxnc.sh -tls '+\
            '-tlskeystore ./configuration/tlsKeyStore -tlstruststore '+\
            './configuration/tlsTrustStore'
            self.run_n = str(self.run_ndb)
            stdin, stdout, stderr = ssh.exec_command(self.run_n)
            time.sleep(30)
            self.prov_pass = 'cd '+xnc_path+'bin/ ;./xnc '+\
                'config-keystore-passwords --user admin '+\
                '--password admin --url https://'+self.tem_serip+\
                ':8443 --verbose --keystore-password '+self.keystore_password+\
                ' --truststore-password '+self.keystore_password
            self.prov_pass_b = str(self.prov_pass)
            stdin, stdout, stderr = ssh.exec_command(self.prov_pass_b)
            time.sleep(10)
            self.login_mulser += 1
            ssh.close()
if __name__ == "__main__":
    os.system('cd')
    dir = os.path.dirname(__file__)
    filename = os.path.join(dir, 'Utilities/Input/inputfile.yaml')
    D1 = Device()
    D1.method_one()
    D1.method_two()
    os.system('rm -rf temp.log')


