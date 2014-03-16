# Copyright (C) 2013 Cisco Systems Inc.
# All rights reserved
'''
Dummy file. Some cisco modules import _cisco module, which is a shared library
on the switch. The library does not work off the box. 

Providing a dummy file so that things compile. However 
cisco_socket.py 
md5sum.py
will not work properly, given they depend on the _cisco shared module.
'''