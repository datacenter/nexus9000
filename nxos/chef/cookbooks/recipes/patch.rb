# Cookbook Name::  cisco Package 
# Recipe:: patch

#
# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
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

 
require 'chef/resource/cisco_device'
require 'chef/provider/cisco_device'
 
require 'chef/resource/cisco_package'
require 'chef/provider/cisco_package'
require 'resolv'
require 'socket'
require 'ipaddr'
 
 
# Sample cookbook to use cisco device and cisco package.
 
name = Socket.gethostname
name = name.split('.')[0]
puts "The host name is #{name}"
 
# create a cisco device
# Resource : CiscoDevice
# resource name: The name of the cisco device to connect to for configuring
# username : user account on the NXK to use for connecting to device
# password :  password for the login 
# action : ":create" , this action results in creating an device object and 
#                   connecting to the NXK device 
#           
 
cisco_device "#{name}" do
  username "admin"
  password "xxxxxx"
  action :create
end
 
 
 
# Resource :  CiscoPackage
# resource name: This attribute is mandatory and format is "device/package_name"
#      - Package name:  the package to be installed/removed 
#                                    
#      - Device name:   the device on which the package to be 
#                                    installed 
#
# source:   The URI of the source file that contains the patch
#                - Note: The file name can be different from package name
#            
# action:  The action function to be invoked on the provider
#           - ":activate" - brings the package to activated state.
#
 
 
  # source "bootflash:///test3.gbin"
cisco_package "EXAMPLE-1-9508-2/n9000_CSCuj11591.gbin" do
 
  source "bootflash:///n9000_CSCuj11591.gbin"
  action :activate
#  action :commit
  
end
 
# Ruby code could be embedded in cookbook
 
begin 
 sleep 1
end
 
 
# Resource :  CiscoPackage
# resource name: This attribute is mandatory and format is "device/package_name"
# action:  The action function to be invoked on the provider
#           - ":remove" - brings the package to removed state.
#
 
 
#cisco_package "TME-1-9508-2/n9000_CSCuj11591.gbin" do
#  action :remove
#end
 
 
# create a cisco device
# Resource : CiscoDevice
# resource name: The name of the cisco device to configure
# action : ":destroy" , this results in disonnecting N3K and deleting the object
#           
 
 
cisco_device "TME-1-9508-2" do
  action :destroy
End
 
