#!/usr/bin/env python

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


import os
import sys
# pysdk should be in the same directory as this script. If not, update this path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pysdk'))

# Import the access library from the insieme python SDK
from insieme.mit import access
# Change the access mode to REST
access.rest()
# Connect to the IFC REST interface and authenticate using the specified credentials 
directory = access.MoDirectory(ip='10.0.0.1', port='8000', user='admin', password='admin')
# Lookup the "universe" object in the object tree, where we can create our tenant object under
uniMo = directory.lookupByDn('uni')
# Create a tenant object (the proper name is fvTenant) under the universe object, and name it MrT
fvTenantMo = directory.create('fv.Tenant', uniMo, name='MrT')
# The created object only exists in memory in this script, until we commit it to the REST interface
directory.commit(fvTenantMo)
