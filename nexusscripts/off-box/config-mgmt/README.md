
#Nexus 9000 Switch Automation tasks

#Automation of Switch Configuration Category
Pre-requisites: Install jinja2 template engine e.g pip install jinja2
Python version > 2.7.*

Scripts are tested on Ubuntu 14.04 release machine.
Nexus Switch version is NXOS: version 6.1(2)I3(1)

Note: If pip does not exist then install it with the command 'sudo apt-get install python-pip'

1. Dynamically update Interface description(for cdp protocol)

  Steps :

     a. Edit the nexus_automation.cfg configuration file with switch host details i.e username,password and email address.
     b. verify the jinja templates exists or not.
     c. schedule the cron job for the python script e.g */15 * * * * cd /home/ubuntu/nexus9000/nexusscripts && python interface_desc_cdp.py

   Note : Follow the above steps to update interface description based on the lldp protocol status. 


2. FEX Configuration

  Steps :

     a. Configuration file is reused from the interface description update (check the host details and email address)
     b. verify the jinja templates exists or not. 
     c. Example inputs to the script : --interface-type ethernet --interface-number 1/20 --fex-number 102
     d. schedule the cron job for the python script e.g */15 * * * * cd /home/ubuntu/nexus9000/nexusscripts && python fex_config.py
