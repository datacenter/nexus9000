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

'''
Dummy file. Some cisco modules import _cisco module, which is a shared library
on the switch. The library does not work off the box. 

Providing a dummy file so that things compile. However 
cisco_socket.py 
md5sum.py
will not work properly, given they depend on the _cisco shared module.
'''