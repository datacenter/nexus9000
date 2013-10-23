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
import xml.dom.minidom
# pysdk should be in the same directory as this script. If not, update this path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pysdk'))

# Import the access library from the insieme python SDK
from insieme.mit import access
# Change the access mode to REST
access.rest()
# Connect to the IFC REST interface and authenticate using the specified credentials 
directory = access.MoDirectory(ip='172.21.197.80', port='8000', user='admin', password='ins3965!')
# Lookup the "universe" object in the object tree, where we can create our tenant object under
uniMo = directory.lookupByDn('uni')
# Create a tenant object (the proper name is fvTenant) under the universe object, and name it MrT
fvTenantMo = directory.create('fv.Tenant', uniMo, name='MrT')

# Create a private L3 routing context for this tenant
fvCtxMo = directory.create('fv.Ctx', fvTenantMo, name='MrTCtx')
# Create a Bridge Domain for the tenant
fvBDMo = directory.create('fv.BD', fvTenantMo, name='BridgeDom')
# Associate the bridge domain and L3 context
fvRsCtx = directory.create('fv.RsCtx', fvBDMo, tnFvCtxName=fvCtxMo.name)
# Add a subnet to the bridge domain
directory.create('fv.Subnet', fvBDMo, ip='10.0.0.1/24')

# Create a Contract and Filter for HTTP trafic
vzBrCPMoHTTP = directory.create('vz.BrCP', fvTenantMo, name='WebContract')
# Create a filter with a single entry for port 80, protocol TCP (6)
filterMo = directory.create('vz.Filter', fvTenantMo, name='WebFilter')
entryMo = directory.create('vz.Entry', filterMo, name='HttpPort')
entryMo.dFromPort = '80'
entryMo.dToPort = '80'
entryMo.prot = '6'
# Add a subject to the contract
vzSubjMo = directory.create('vz.Subj', vzBrCPMoHTTP, name='WebSubject')
# Associate the subject and filter
directory.create('vz.RsSubjFiltAtt', vzSubjMo, tDn=filterMo.getDn())

# Create a Contract and Filter for SQL traffic
vzBrCPMoSQL = directory.create('vz.BrCP', fvTenantMo, name='SqlContract')
filterMo = directory.create('vz.Filter', fvTenantMo, name='SqlFilter')
entryMo = directory.create('vz.Entry', filterMo, name='SqlPort')
entryMo.dFromPort = '1521'
entryMo.dToPort = '1521'
entryMo.prot = '6'
vzSubjMo = directory.create('vz.Subj', vzBrCPMoSQL, name='WebSubject')
directory.create('vz.RsSubjFiltAtt', vzSubjMo, tDn=filterMo.getDn())

# Create a new application profile named WebApp
fvApMo = directory.create('fv.Ap', fvTenantMo, name='WebApp')
# Create a web EPG
fvAEPgMoWeb = directory.create('fv.AEPg', fvApMo, name='WebEPG')
# Associate the web EPG and Bridge Domain we created
directory.create('fv.RsBd', fvAEPgMoWeb, tnFvBDName=fvBDMo.name)
# Consume the SQL contract
directory.create('fv.RsCons', fvAEPgMoWeb, tDn=vzBrCPMoSQL.getDn())
# Provide the Web contract
directory.create('fv.RsProv', fvAEPgMoWeb, tDn=vzBrCPMoHTTP.getDn())

# Create an EPG for SQL
fvAEPgMoSQL = directory.create('fv.AEPg', fvApMo, name='SqlEPG')
directory.create('fv.RsBd', fvAEPgMoSQL, tnFvBDName=fvBDMo.name)
directory.create('fv.RsProv', fvAEPgMoSQL, tDn=vzBrCPMoSQL.getDn())

# Print out the XML representation of the tenant data model we just built with the SDK
print('posting: %s' % xml.dom.minidom.parseString(fvTenantMo.toXML()).toprettyxml())

# The created object only exists in memory in this script, until we commit it to the REST interface
directory.commit(fvTenantMo)
