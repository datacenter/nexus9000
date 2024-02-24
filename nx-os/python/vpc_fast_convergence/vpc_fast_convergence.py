from cli import cli, clid
from time import sleep
import json
import argparse
import syslog
import logging
import sys

logging.basicConfig(level=logging.INFO, format="vPC Fast Convergence: %(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SLEEPTIMER = 300
# Sleep timer to wait vPC convergence, default is 300 seconds
DELAYUPTIMER = 5
# Delay timer to no shutdown delay for each vPC member port, default is 5 seconds


def vpc_fast_convergence(delay_timer, delay_port_timer):
    try:
        result = json.loads(clid('show vpc'))
        vpc_ports = result['TABLE_vpc']['ROW_vpc']
    except Exception as e:
        syslog.syslog(3, 'vpc_fast_convergence: Unable to get vPC member ports, Error: %s' % e)
        sys.exit(0)

    syslog.syslog(3, 'vpc_fast_convergence: Will shutdown all vPC member ports to wait vPC convergence!')
    for i in vpc_ports:
        cli('conf t ; interface %s ; shutdown' % i['vpc-ifindex'])
    sleep(delay_timer)

    syslog.syslog(3, 'vpc_fast_convergence: Start up all vPC member ports!')
    for i in vpc_ports:
        port = i['vpc-ifindex']
        try:
            cli('conf t ; interface %s ; no shutdown' % port)
        except KeyboardInterrupt:
            logger.info("User interrupt, exiting!")
            sys.exit(0)
        except Exception as e:
            syslog.syslog(3, 'vpc_fast_convergence: Unable to no shutdown vPC member ports %s, Error: %s' % (port, e))
            pass
        sleep(delay_port_timer)


def install_script():
    try:
        cli('conf t ; event manager applet vpc_fast_convergence ; \
                        event syslog pattern \"Module 1 is online\" ; \
                        action 1 cli python bootflash:vpc_fast_convergence.py enable')
        logger.info("Script installed successfully. "
                    "Automatic backup of running configuration to startup configuration is in progress.")
        cli('copy running-config startup-config')
    except Exception as e:
        logger.error('Install script failed, please try later! Error: %s' % e)


def uninstall_script():
    try:
        cli('conf t ; no event manager applet vpc_fast_convergence')
        logger.info("Script uninstalled successfully. "
                    "Automatic backup of running configuration to startup configuration is in progress.")
        cli('copy running-config startup-config')
    except Exception as e:
        logger.error('Uninstall script failed, please try later! Error: %s' % e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("option", help="install/uninstall",
                        type=str)
    args = parser.parse_args()
    if args.option == "enable":
        # enable is a hidden option for EEM applet only
        vpc_fast_convergence(SLEEPTIMER, DELAYUPTIMER)
    elif args.option == "install":
        install_script()
    elif args.option == "uninstall":
        uninstall_script()
    else:
        logger.error("Invalid option, please use install or uninstall!")


if __name__ == '__main__':
    main()
