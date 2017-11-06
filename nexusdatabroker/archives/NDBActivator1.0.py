from cli import *
import json
import os,sys
import subprocess
import optparse
import logging
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
con_log_handler = logging.StreamHandler()
file_log_handler = logging.FileHandler("/bootflash/ndb_deploy.log")
file_log_handler.setLevel(logging.DEBUG)
con_log_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log_handler.setFormatter(formatter)
con_log_handler.setFormatter(formatter)
logger.addHandler(file_log_handler)
logger.addHandler(con_log_handler)


def get_iface_info(vservice_name):
    try:
        iface_details=json.loads(clid("show int mgmt 0"))
        data = iface_details['TABLE_interface']['ROW_interface']
    except Exception as error:
        logger.error("Show command failed")
        sys.exit()

    mac_addr = data['eth_hw_addr'].replace('.', '')
    mac_addr = ':'.join(mac_addr[i:i+2] for i in range(0, len(mac_addr), 2))

    data ="mgmt0.multicast=false\nmgmt0.mtu=" + data['eth_mtu'] + \
          "\nmgmt0.mac=" + mac_addr + "\nmgmt0.addresses=0\nmgmt0.0.ip=" + \
          data['eth_ip_addr'] + "\nmgmt0.0.prefix=" + str(data['eth_ip_mask'])

    with open('/bootflash/interfaces', 'w') as fd:
        fd.write(data)

    cont_path ='/isan/vdc_1/virtual-instance/' + vservice_name + '/rootfs'

    if os.path.isdir(cont_path):
        os.chdir(cont_path)
        dir_name = 'embndb'
        if not os.path.exists(dir_name):
            subprocess.call(['sudo', 'mkdir', dir_name])
    else:
        logger.error("Please provide proper virtual-service name")
        sys.exit()

    os.chdir(cont_path+ '/' + dir_name)
    subprocess.call(['sudo', 'cp', cont_path+'/xnclite/launcher.sh', 'interfaces']) #To get required permission 
    subprocess.call(['sudo', 'cp', '/bootflash/interfaces', 'interfaces'])          #Override the file which has the permission
    subprocess.call(['sudo', 'rm', '/bootflash/interfaces'])          # cleanup tmp interface file
    logger.info("Successfully created /embndb/interface file with management interface details")

def creater_launcher_file(vservice_name):
    cont_path ='/isan/vdc_1/virtual-instance/' + vservice_name + '/rootfs'
    with open(cont_path+'/xnclite/xnc/version.properties') as properties_fd:
                for line in properties_fd:
                        line = line.strip()
                        if "com.cisco.csdn.xnc.version" in line:
                                version = line.split("=")[1].strip()
    
    def str_to_raw(s):
                raw_map = {8:r'\b', 7:r'\a', 12:r'\f', 10:r'\n', 13:r'\r', 9:r'\t', 11:r'\v'}
                return r''.join(i if ord(i) > 32 else raw_map.get(ord(i), i) for i in s)

    if version in '3.0.0' or version in '3.1.0':
     with open(cont_path+'/xnclite/launcher.sh', 'r') as input_file, open('/bootflash/tmp_launcher.sh', 'w') as output_file:
	for line in input_file:
           if '/tmp/netclient.log' in line.strip():
                old ='/tmp/netclient.log'
                new ='/embndb/launcher.log'
                output_file.write(line.replace(old, new))

           elif 'IPADDRESS=' in line.strip():
                line = str_to_raw(line)
                new_line_1 = "\tfile=\"/embndb/interfaces\"\n"
                new_line_1 = new_line_1.expandtabs(4)
                output_file.write(new_line_1)
                new_line_1 = "\tif [ -e \"$file\" ]\n"
                new_line_1 = new_line_1.expandtabs(4)
                output_file.write(new_line_1)
                new_line_1 = "\tthen\n"
                new_line_1 = new_line_1.expandtabs(4)
                output_file.write(new_line_1)
                new_line_1 = "IPADDRESS=`grep -o -E '\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b' /embndb/interfaces`"
                new_line_1 = str_to_raw(new_line_1)
                new_line_1 = "\t"+new_line_1
                new_line_1 = new_line_1.expandtabs(8)
                output_file.write(new_line_1)
                new_line_1 = "\n\techo \"$IPADDRESS\"\n"
                new_line_1 = new_line_1.expandtabs(8)
                output_file.write(new_line_1)
                new_line_1 = "\telse\n"
                new_line_1 = new_line_1.expandtabs(4)
                output_file.write(new_line_1)
                new_line_1 = "\techo \"Management IP address is not available, reach out to admin\"\n"
                new_line_1 = new_line_1.expandtabs(8)
                output_file.write(new_line_1)
                new_line_1 = "\texit 1\n"
                new_line_1 = new_line_1.expandtabs(8)
                output_file.write(new_line_1)
                new_line_1 = "\tfi\n"
                new_line_1 = new_line_1.expandtabs(4)
                output_file.write(new_line_1)

    
           elif 'onepproxylogfile=' in line.strip():
		new_line_1 = ""
		output_file.write(new_line_1)

	   elif 'lib/netclient' in line:
		new_line_1 = ""
                output_file.write(new_line_1)
	   elif 'onepproxylogfile' in line and 'touch' in line:
		new_line_1 = ""
                output_file.write(new_line_1)
	   elif 'onepproxylogfile' in line and 'rm' in line:
		new_line_1 = ""
                output_file.write(new_line_1)
	   elif '-Dcom.cisco.xnclite.interface.properties.file' in line:
		old ='/tmp/interfaces'
		new ='/embndb/interfaces'
		output_file.write(line.replace(old, new))
	   else:
                output_file.write(line) 
     subprocess.call(['sudo', 'cp', '/bootflash/tmp_launcher.sh', cont_path+'/xnclite/launcher.sh'])
     subprocess.call(['sudo', 'rm', '/bootflash/tmp_launcher.sh'])
     logger.info("Successfully updated /xnclite/launcher.sh file") 
    elif "2" in version.split(".")[0]:
        logger.info("Not supported version,please upgrade to the newer version")   

def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-v", "--vservice_name",
                      help="Mandatory Arg: Specify the existing virtual service name ")
    (options, args) = parser.parse_args()
    if options.vservice_name==None: 
        logger.error("Please provide proper arguements. Use -h option for more details")
        sys.exit()

    get_iface_info(options.vservice_name)

    creater_launcher_file(options.vservice_name)

if __name__ == "__main__":
    main()


