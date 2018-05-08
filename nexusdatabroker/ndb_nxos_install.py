import re
import cli
import sys
import logging
import optparse
COMMAND_LIST = []
STRICT_LOG_FILE = True
if '--debug' in sys.argv:
    STRICT_LOG_FILE = False
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    CON_LOG_HANDLER = logging.StreamHandler()
    FILE_LOG_HANDGLER = logging.FileHandler('/bootflash/ndb_nxos_install.log')
    FILE_LOG_HANDGLER.setLevel(logging.DEBUG)
    CON_LOG_HANDLER.setLevel(logging.DEBUG)
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    FILE_LOG_HANDGLER.setFormatter(FORMATTER)
    CON_LOG_HANDLER.setFormatter(FORMATTER)
    logger.addHandler(FILE_LOG_HANDGLER)
    logger.addHandler(CON_LOG_HANDLER)
elif len(sys.argv) == 1:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    FILE_LOG_HANDGLER = logging.FileHandler('/bootflash/ndb_nxos_install.log')
    FILE_LOG_HANDGLER.setLevel(logging.DEBUG)
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    FILE_LOG_HANDGLER.setFormatter(FORMATTER)
    logger.addHandler(FILE_LOG_HANDGLER)
else:
    usage = 'usage: %prog [options]'
    PARSER = optparse.OptionParser(usage=usage)
    PARSER.add_option(
        '--debug',
        action='store_true',
        help='Optional Arg: Specify the debug logs'+\
             ' in both console and log file ')
    (options, args) = PARSER.parse_args()

    print'Invalid argument. Plesae use -h option for more details.'
    sys.exit(0)
try:
    NXOS = cli.cli('show version | inc NXOS | inc version')
    PLATFORM = cli.cli('show version | inc ignore-case Chassis')
except BaseException:
    logger.error(
        'Something went wrong while fetching switch platform and nxos')
    sys.exit(0)


def enter_mode():
    mode = raw_input('Enter mode(NXAPI):')
    if STRICT_LOG_FILE:
        print'Validating mode.Please wait..'
    if mode == '':
        mode = 'NXAPI'
        logger.info('Mode: ' + ' ' + mode)
    else:
        validate_mode(mode)
        logger.info('Mode:' + ' ' + mode)


def validate_mode(mode):
    if mode.lower() == 'nxapi' or mode.lower() == 'nx':
        pass
    else:
        logger.error('Enter valid mode')
        sys.exit(0)


def add_span():
    try:
        cli.cli('configure terminal ; spanning-tree mode mst')
        logger.info('spanning-tree mode mst' +
                    ' command executed successfully')
        cli.cli('configure terminal ; vlan configuration 1-3967')
        logger.info('vlan configuration 1-3967' +
                    ' command configured successfully')
        cli.cli(
            'configure terminal ; no spanning-tree vlan 1-3967')
        logger.info(
            'no spanning-tree vlan 1-3967' +
            ' command configured successfully')
    except BaseException:
        logger.error('Something went wrong while' +
                     'executing spanning tree and vlan configuration')
        sys.exit(0)


def install():
    if '3548' in PLATFORM or '3048' in PLATFORM:
        logger.error(
            'Current Switch platform' +
            ' ' +
            'does not support NXAPI')
        sys.exit(0)
    elif '9000' not in PLATFORM:
        platform = validate_platform()
        if platform:
            get_device_ip()
            get_version()
            enter_mode()
            add_span()
            add_banner()
            add_hardware_config()
        else:
            logger.error('Device not supported')
            sys.exit(0)
    else:
        get_device_ip()
        get_version()
        enter_mode()
        add_span()
        add_banner()
        add_hardware_config()


def validate_platform():
    try:
        if 'N3K' in cli.cli('sh module'):
            return True
        else:
            return False
    except BaseException:
        logger.error('Caught exception whle validting switch platform')
        sys.exit(0)


def add_banner():
    banner_name = raw_input('Enter banner message:')
    result = validate_banner(banner_name)
    try:
        if result:
            cli.cli('configure terminal ; banner motd' + ' ' + banner_name)
            logger.info('banner added successfully')
        else:
            banner_name = banner_name[0:] + banner_name[0]
            cli.cli('configure terminal ; banner motd' + ' ' + banner_name)
            logger.info('banner added successfully')
    except BaseException:
        logger.error('Something went wrong while adding banner message')
        sys.exit(0)


def validate_banner(banner):
    if banner == '':
        logger.error('Enter valid banner message')
        sys.exit(0)
    for i in banner[1:]:
        if banner[0] == i:
            return True
    return False


def add_hardware_config():
    if '9000' in PLATFORM or '3164' in PLATFORM or '32' in PLATFORM:
        if '92' in PLATFORM or ('93' in PLATFORM and 'EX' in PLATFORM):
            ing_tcam = raw_input(
                'Enter hardware access-list tcam region ing-ifacl:')
            validate_tcam(ing_tcam)
            if 'double-wide' in ing_tcam:
                logger.error('double-wide not supported for platform')
                sys.exit(0)
            if STRICT_LOG_FILE:
                print'Configuration is being added. Please wait..'
            try:
                cli.cli('configure terminal ; feature nxapi')
                logger.info('feature nxapi command executed successfully')
            except BaseException:
                logger.error('feature nxapi command execution failed')
                sys.exit(0)
            try:
                cli.cli(
                    'configure terminal' +
                    ' ; hardware access-list tcam region ing-ifacl' +
                    ' ' +
                    ing_tcam)
                logger.info(
                    'ing-ifacl tcam region' +
                    ' configured successfully')
            except BaseException:
                logger.error(
                    'Failed to configure ing-ifacl' +
                    ' Tcam region exceeded')
                sys.exit(0)
            cli.cli('copy running-config startup-config')
            logger.info('Configuration copied to startup')
            logger.info('Reload the switch' +
                        ' for configuration to take effect')

        else:
            ifacl_tcam = raw_input(
                'Enter hardware access-list tcam region ifacl:')
            validate_tcam(ifacl_tcam)
            ipv6_tcam = raw_input(
                'Enter hardware access-list tcam region ipv6-ifacl:')
            validate_tcam(ipv6_tcam)
            mac_tcam = raw_input(
                'Enter hardware access-list tcam region mac-ifacl:')
            validate_tcam(mac_tcam)
            if STRICT_LOG_FILE:
                print'Configuration is being added. Please wait..'
            try:
                cli.cli('configure terminal ; feature nxapi')
                logger.info('feature nxapi command executed successfully')
            except BaseException:
                logger.error('feature nxapi command execution failed')
                sys.exit(0)
            try:
                cli.cli(
                    'configure terminal' +
                    ' ; hardware access-list tcam region ifacl' +
                    ' ' +
                    ifacl_tcam)
                COMMAND_LIST.append(
                    'hardware access-list tcam region ifacl')
                logger.info(
                    'ifacl tcam region' +
                    ' configured successfully')
            except BaseException:
                logger.error(
                    'Failed to configure ifacl ' +
                    ' .Tcam region exceeded')
                sys.exit(0)
            try:
                cli.cli(
                    'configure terminal' +
                    ' ; hardware access-list tcam region ipv6-ifacl' +
                    ' ' +
                    ipv6_tcam)
                COMMAND_LIST.append(
                    'hardware access-list tcam region ipv6-ifacl')
                logger.info(
                    'ipv6-ifacl tcam region' +
                    ' configured successfully')
            except BaseException:
                remove_config(COMMAND_LIST[0], ifacl_tcam)
                logger.error(
                    'Failed to configure ipv6-ifacl' +
                    ' .Tcam region exceeded')
                sys.exit(0)
            try:
                cli.cli(
                    'configure terminal' +
                    ' ; hardware access-list tcam region mac-ifacl' +
                    ' ' +
                    mac_tcam)
                COMMAND_LIST.append(
                    'hardware access-list tcam region mac-ifacl')
                logger.info(
                    'mac-ifacl tcam region' +
                    ' configured successfully')
            except BaseException:
                remove_config(COMMAND_LIST[0], ifacl_tcam)
                remove_config(COMMAND_LIST[1], ipv6_tcam)
                logger.error(
                    'Failed to configure mac-ifacl' +
                    ' .Tcam region exceeded')
                sys.exit(0)
            cli.cli('copy running-config startup-config')
            logger.info('Configuration copied to startup')
            logger.info('Reload the switch' +
                        ' for configuration to take effect')

    else:
        ifacl_tcam = raw_input(
            'Enter hardware profile tcam region ifacl:')
        validate_tcam(ifacl_tcam)
        if STRICT_LOG_FILE:
            print'Configuration is being added. Please wait..'
        try:
            cli.cli('configure terminal ; feature nxapi')
            logger.info('feature nxapi command executed successfully')
        except BaseException:
            logger.error('feature nxapi command executed failed')
            sys.exit(0)
        try:
            cli.cli('configure terminal' +
                    ' ;  hardware profile tap-aggregation')
            logger.info(
                'hardware profile tap-aggregation' +
                'command executed successfully')
            COMMAND_LIST.append('hardware profile tap-aggregation')
        except BaseException:
            logger.error('hardware profile tap-aggregation' +
                         ' command execution failed')
            sys.exit(0)
        try:
            cli.cli(
                'configure terminal' +
                ' ; hardware profile tcam region ifacl' +
                ' ' +
                ifacl_tcam)
            COMMAND_LIST.append('hardware profile tcam region ifacl')
            logger.info(
                'ifacl tcam region' +
                'configured successfully')
        except BaseException:
            remove_config(COMMAND_LIST[0], '')
            logger.error(
                'Failed to configure ifacl' +
                ' .Tcam region exceeded')
            sys.exit(0)
        cli.cli('copy running-config startup-config')
        logger.info('Configuration copied to startup')
        logger.info('Reload the switch' +
                    ' for configuration to take effect')


def remove_config(command, size):
    if size == '':
        try:
            cli.cli('configure terminal ; no' + ' ' + command)
        except BaseException:
            logger.error('Failed to remove configuration')
            sys.exit(0)
    else:
        try:
            cli.cli('configure terminal ; no' + ' ' + command + ' ' + size)
        except BaseException:
            logger.error('Failed to remove configuration')
            sys.exit(0)


def validate_tcam(tcam_value):
    if 'double-wide' in tcam_value:
        if tcam_value.split(' ')[0].isdigit():
            pass
        else:
            logger.error('Enter valid number for tcam')
            sys.exit(0)
        if int(tcam_value.split(' ')[0]) % 256 == 0:
            pass
        else:
            logger.error('TCAM size should be in multiple of 256 entries')
            sys.exit(0)
    elif tcam_value.isdigit():
        if int(tcam_value.split(' ')[0]) % 256 == 0:
            pass
        else:
            logger.error('TCAM size should be in multiple of 256 entries')
            sys.exit(0)
    else:
        logger.error('Enter valid number for tcam')
        sys.exit(0)


def get_device_ip():
    ip_command = cli.cli('sh run interface mgmt0 | grep ip').split(' ')
    ip_address = ip_command[4].split('/')[0]
    logger.info('Device IP -' + ' ' + ip_address)


def get_version():
    list1 = cli.cli('show version | inc NXOS | inc version').split(' ')
    version = list1[4].split('\n')[0]
    logger.info('NXOS Version -' + ' ' + version)

def interface_parser(out):
    interfaces = {'Ethernet' : [], 'port-channel': [] }
    lines = out.replace('\\r', '')
    lines = lines.replace('\r','')
    lines = lines.replace('\\n','\n')
    lines = lines.split("\n\n")
    for line in lines:
        line = line.strip(" ")
        if re.search(r'(interface)\s+(.*)',line,re.IGNORECASE):            
            value = re.search(r'(interface)\s+(.*)',line,re.IGNORECASE)
            interface_name = value.group(2)
            if 'Ethernet' in interface_name:
                interfaces['Ethernet'].append(interface_name)
            elif 'port-channel' in interface_name:
                interfaces['port-channel'].append(interface_name)
    return interfaces    

def main():
    try:
        while True:
            operation = raw_input("Do you want to shut/unshut all interfaces [shut(S)/unshut(U)/no_action(N)] - ")
            if operation in ['S','U']:
                interfaces = cli.cli('sh run int | no-more')
                interface_response = interface_parser(interfaces)
                interface_names = ''
                if len(interface_response['port-channel']) != 0:
                    interface_names = ','.join(interface_response['port-channel'])
                    if operation == 'S':
                        cli.cli('configure terminal ; interface '+ interface_names + ' ; shutdown ; end')
                        logger.info("Successfully shutted down the port-channel interfaces")
                    elif operation == 'U':
                        cli.cli('configure terminal ; interface '+ interface_names + ' ; no shutdown ; end')
                        logger.info("Successfully unshutted the port-channel interfaces")
                if len(interface_response['Ethernet']) != 0:
                    interface_names = ','.join(interface_response['Ethernet'])
                    if operation == 'S':
                        cli.cli('configure terminal ; interface '+ interface_names + ' ; shutdown ; end')
                        logger.info("Successfully shutted down the ethernet interfaces")
                    elif operation == 'U':
                        cli.cli('configure terminal ; interface '+ interface_names + ' ; no shutdown ; end')
                        logger.info("Successfully unshutted the ethernet interfaces")
                    
                break
            elif operation == 'N':
                break
            else:
                print "Invalid input"
            
    except BaseException:
        logger.error(
            'Something went wrong while fetching switch platform and nxos')
        sys.exit(0)    
    install()

if __name__ == '__main__':
    main()

