Nexus 9000 Partner Demo Scripts
===============================
Welcome to the OneCloud Consulting Nexus 9000 demo script repository.

These scripts were developed and tested on a Nexus 9000 C9372PX chassis running 7.0(3)I1(2).

Summary
========
1. __find_freeip.py__ : Pings a range of IP addresses then prints which are UP followed by a summary of addresses that are unused.
2. sh_switch_details.py : Displays specific details from neighbor based on its IP address. Demonstrates use of a single programmatic Python instruction versus a series of CLI commands to obtain the same information.
3. cdp.py : Configures interface descriptions based on CDP information.
4. lldp.py : Configured interface descriptions based on LLDP information.
5. ospf.py : Provides menu driven options to configure OSPF interface attributes (area/cost).
6. pim.py : Provides menu driven options to configure PIM  interface attributes.
7. cleanup.py : Provides menu driven options to cleanup demo configurations.
8. sh_version.py : Uses NX-API to compare expected NX-OS version against actual NX-OS versions running in the network.
9. sh_proc_cpu_sort.py : Checks CPU health of switch at regular intervals with option to log output to file for TAC.
10. sh_proc_mem.py : Checks memory utilization of switch at regular intervals with option to log to file for TAC.
11. sh_int_count.py : Checks interface packet count at regular intervals with option to log to file for TAC.

