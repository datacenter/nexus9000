
#Nexus 9000 Switch Automation tasks

#Automation of Switch Monitoring Category
Pre-requisites: Install jinja2 template engine e.g pip install jinja2
Python version > 2.7.*

Scripts are tested on Ubuntu 14.04 release machine.

Note: If pip does not exist then install it with the command 'sudo apt-get install python-pip'

1. Interface monitoring 

  Steps :

     a. Edit the nexus_automation.cfg configuration file with switch host details,slot/port details and email address.
     b. verify the jinja templates exists or not.
     c. schedule the cron job for the python script e.g */15 * * * * cd /home/ubuntu/Nexus9k_Sailaja/nexus9000/nexusscripts && python interface_monitor.py

  Note : 

       The existing script is to monitor interface slots 1&2 with the specified port range(config file).If there are more slots then modify the source code 'interface_monitor.py' accordingly along with the jinja template 'interface_10.1.150.12_.jinja' in the templates directory. 
  

2. Sytem-Level Resources monitoring

  Steps :

     a. Configuration file is reused from the interface monitoring (check the host details and email address)
     b. verify the jinja templates exists or not. 
     c. schedule the cron job for the python script e.g */15 * * * * cd /home/ubuntu/Nexus9k_Sailaja/nexus9000/nexusscripts && python systemresc_monitor.py
