#Nexus 9000 Switch Automation tasks

#Automation of Switch Monitoring Category
Python version > 2.7.*

Nexus Switch version is NXOS: version 6.1(2)I3(1)


1. Interface monitoring

  Steps :

     a. Edit the nexus_automation.cfg configuration file with switch host details,slot/port details.

  Note :

       The existing script is to monitor interface slots 1&2 with the specified port range(config file).If there are more slots then modify the source code 'interface_m


2. Sytem-Level Resources monitoring

  Steps :

     a. Configuration file is reused from the interface monitoring (check the host details)

