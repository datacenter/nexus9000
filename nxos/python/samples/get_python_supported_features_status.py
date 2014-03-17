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
#    source get_python_supported_features_status.py
#
# or it can be run by python natively from NX-OS (VSH):
#
#    python bootflash:///scripts/get_python_supported_features_status.py
#
# or from Bash:
#
#    run bash
#    python /bootflash/scripts/get_python_supported_features_status.py
#

# For formatting the output
import string
# This is all we need to import from the cisco package
from cisco.feature import Feature

print ""
print "Python supported features status:"
print "=" * 68

# Get all the features that python can play with on this device
# Feature.allSupportedFeatures()returns those features as a list of strings
for afeature in Feature.allSupportedFeatures():
    # Setup a temporary string
    temp_string = ""
    # Use the cisco.feature.FeatureFactory to create a temporary object based
    # on the feature name
    temp_feature_obj = Feature.get(afeature)
    # See if the feature is enabled or disabled
    status = temp_feature_obj.is_enabled()
    # Build the output string, start by adding the feature name to it, left
    # justified, padded by white space to ensure 11 characters
    temp_string += string.ljust(afeature, 11)
    # Now add the word "is", centered and padded with space to ensure 3
    # characters
    temp_string += string.center("is", 3)
    # Now add the 'Enabled' or 'Disabled' string depending on the status
    # using a ternary operator, right justified and padded with white
    # space to ensure at least 11 characters
    temp_string += string.rjust(("Enabled" if Feature.get(afeature).is_enabled() else
        "Disabled"), 11)
    print temp_string

print ""