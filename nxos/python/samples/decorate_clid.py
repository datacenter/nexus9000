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
#

# This script shows how to use a decorator to change the behavior of the clid
# function from returning a string (which is the default for the 6.1(2)I1(1)
# image on the Nexus 9000) to returning a dictionary.  If this script is
# installed in bootflash://scripts on the Nexus 9000, it can be run using the
# source command:
#
#    source decorate_clid.py
#
# Or it can be run using python from NX-OS (VSH):
#
#    python bootflash:///scripts/decorate_clid.py
#
# Or using python from bash:
#
#    run bash
#    python /bootflash/scripts/decorate_clid.py
#
# Example output:
#
# Switch# source decorate_clid.py
# Type of original clid output: <type 'str'>
# Type of new clid output: <type 'dict'>
# Switch#
#

import json
from cli import *

# Here's our decorator.  The wrapper simply wraps the previous
# function in a json.loads() call to load the json encoded
# string into a dictionary and then returns it.
def dict_decorator(target_function):
    def wrapper(cmd):
        return json.loads(target_function(cmd))
    return wrapper

# Let's see how the current beahvior is.
original = clid("show interface brief")
print "Type of original clid output: " + str(type(original))

# This doesn't use the @ decorator syntax but it _is_ a
# decorator none the less.
clid = dict_decorator(clid)

# Let's see what our decorator does
new = clid("show interface brief")
print "Type of new clid output: " + str(type(new))