# vPC Fast Convergence

## Description
The `vpc_fast_convergence.py` script is designed to introduce a delay in bringing up the VPC (Virtual Port Channel) on Cisco Nexus 9000 switches running NX-OS. This script is useful in scenarios where you want to ensure that certain conditions are met before the VPC is fully operational. 

In version 9.x and previous switches, when the vPC Peer switch reboots up, the peer-link of vPC will switch the traffic over immediately, at this time, because some interfaces have not been fully initialized, it will lead to traffic loss. 

In order to solve this problem, we can `shutdown` the vPC member ports first, and then `no shutdown` vPC member ports one by one after the initialization is completed.

There are a few known issues or enhancements related to VPC convergence, some of them are listed below:
[CSCvw14768 10 seconds Packet loss observed when VPC peer is joining back VPC after reload](https://bst.cloudapps.cisco.com/bugsearch/bug/CSCvw14768)

[CSCvu13461 Packet loss for seconds when VPC leg bring up](https://bst.cloudapps.cisco.com/bugsearch/bug/CSCvu13461)

[CSCwa20455 N9K : spanning-tree vPC convergence code commit to kr3f_dev](https://bst.cloudapps.cisco.com/bugsearch/bug/CSCwa20455)

Upgrade to the latest version of NX-OS to get the latest fixes and enhancements always the best practice. But if you are not able to upgrade, you can use this script to avoid the packet loss issue. But please test it in your lab environment before deploying it in production.

## Prerequisites
- Python 3.x
- Cisco Nexus 9000 switch running NX-OS
- TOR switch only

## Usage
1. Clone the repository or download the `vpc_fast_convergence.py` script.
2. Copy the script to the switch using SCP or any other method.
3. Run the script using the following command to install it on the switch, EEM applet will be created to run the script when Module 1 is online:
    ```
    N9K# python3 vpc_fast_convergence.py install
    ```
4. To uninstall the script, run the following command:
    ```
    N9K# python3 vpc_fast_convergence.py uninstall
    ```
5. To check the status of the script, run the following command:
    ```
    N9K# sh run eem

    !Command: show running-config eem
    !Running configuration last done at: Sat Feb 24 18:50:03 2024
    !Time: Sat Feb 24 18:50:10 2024
    
    version 9.3(12) Bios:version 05.47 
    event manager applet vpc_fast_convergence
      event syslog pattern "Module 1 is online"
      action 1 cli python bootflash:vpc_fast_convergence.py enable
    
    ```
6. Please DO NOT use `enable` option if you are not sure about the script. It will enable the script and it will start delaying the VPC convergence.This may cause network outage.