# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
import sys

sys.path.append("./cisco")
sys.path.append("./utils")

from nxapi_utils import NXAPITransport 
from cisco.interface import Interface

################### 
# NXAPI init block
###################
target_url = "http://10.30.14.8/ins"
username = "admin"
password = "admin"
NXAPITransport.init(target_url=target_url, username=username, password=password)
###################

################### 
# cli/clip/clid are changed a bit, but largely the same
###################
print NXAPITransport.cli("show version")

NXAPITransport.clip("show interface brief")

NXAPITransport.clic("conf t ;interface eth4/1 ;no shut")

print NXAPITransport.clid("show version")

################### 
# Below is exactly the same as the usage on the switch. Do whatever you
# are already doing on the switch right now!
###################
print Interface.interfaces()

i = Interface("Ethernet4/1")

print i.show(key="eth_mtu")

i.set_description(d="ifx4/1")



