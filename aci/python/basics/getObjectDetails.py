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
from argparse import ArgumentParser

# pysdk should be in the same directory as this script. If not, update this path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pysdk'))

def printInfo(o,d=0):
	# Print some spaces based on depth, and the distinguished name of the object
	print ' ' * (d*4), o.getDn()
	# Print the type of the object
	print ' ' * ((d*4)+1), 'type: %s' % (o.getClass().getName())
	# Print the names and values of the objects properties
	for p in o.getProperties():
		n = p.getName()
		v = o.getPropertyValue(p.getName())
		if v is not '':
			print ' ' * ((d*4)+2), '%s: %s' % (n, v)

def queryObjects(moDir, objects, limit, depth=0):
	for o in objects:
		# Print the details for this object
		printInfo(o,depth)
		# if we haven't reached our depth limit, recurse through the children of this object and print it's details
		if depth < limit:
			moDir.fetchChildren(o)
			queryObjects(moDir, o.getChildren(), limit, depth + 1)

def main():
	parser = ArgumentParser(str(__file__))
	parser.add_argument('-i', '--ip', help='IFC IP Address', default='172.21.197.80')
	parser.add_argument('-p', '--port', help='IFC Port', default='8000')
	parser.add_argument('-U', '--username', help='Username', default='admin')
	parser.add_argument('-P', '--password', help='Password', default='ins3965!')
	parser.add_argument('-o', '--object', help='Object class to query for (e.g., fvTenant, infraInfra)', required=True)
	parser.add_argument('-d', '--depth', help='Query depth: How many levels under the top level object to query', default=2)
	args = parser.parse_args()

	# Import the access library from the insieme python SDK
	from insieme.mit import access
	# Change the access mode to REST
	access.rest()
	# Connect to the IFC REST interface and authenticate using the specified credentials 
	directory = access.MoDirectory(ip=args.ip, port=args.port, user=args.username, password=args.password)
	depth = int(args.depth)

	# Query the IFC for object type passed as argument and print depth specified
	tenants = directory.lookupByClass(args.object)
	queryObjects(directory, tenants, depth)

if __name__ == '__main__':
	main()

