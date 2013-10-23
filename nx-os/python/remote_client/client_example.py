# Copyright (C) 2013 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#      http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 

import sys

sys.path.append("./cisco")
sys.path.append("./utils")

from nxapi_utils import NXAPI
from cisco.interface import Interface

################### 
# NXAPI init block
###################
target_url = "http://10.30.14.63/ins"
username = "admin"
password = "admin"
NXAPI.init(target_url=target_url, username=username, password=password)
###################

################### 
# Below is exactly the same as the usage on the switch. Do whatever you
# are already doing on the switch right now!
###################
print Interface.interfaces()

i = Interface("Ethernet4/1")
print i.show(key="eth_mtu")

i.set_description(d="ifx4/1")
