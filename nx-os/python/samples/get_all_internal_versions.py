#!/usr/bin/env python
#
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

# This script can be saved to bootflash:///scripts and then run via:
#
#    source get_all_internal_versions.py
#
# The script will get the output of show module, get the
# module number of every component, then print the output of
#            show hardware internal dev-version
# for every component
#

from cli import *
import json

# clid does not produce a dictionary on the Nexus 9000, it
# produces a json encoded string so load it into a dictionary
showmodout=json.loads(clid('show module'))

modlist = []

# Create a list of module number populated with components
# This gets most of everything, including sups, system controllers,
# fabric modules, linecards, ets.
for modrow in showmodout["TABLE_modwwninfo"]["ROW_modwwninfo"]:
    modlist.append(modrow["modwwn"])

# If we have at least one component to print out (which we should)
# print out a string a hypens for consistency
if len(modlist) > 0:
    print "-" * 68
    
for mod in modlist:
    # Label each out put so we know which output goes where.
    print "Internal version for module " + mod
    print "-" * 68
    clip("slot " + mod + " show hardware internal dev-version")
    print "-" * 68