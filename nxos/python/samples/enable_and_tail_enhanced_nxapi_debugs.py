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

# This script can be used to quickly and easily enable and monitor nx-api
# sessions and debugs on a Nexus 9000 Standalone Switch.  If the script
# is copied into bootflash:///scripts, it can be run as:
#
#    source enable_and_tail_enhanced_nxapi_debugs
#

import os
import sys
import time

def touch(path):
    """ Touch the path, which means create it if it doesn't exist and set the
        path's utime.
    """
    with open(path, 'a'):
        os.utime(path, None)

def get_root(file):
    """ Returns the root filesystem designator in a non-platform-specific way
    """
    somepath = os.path.abspath(sys.executable)
    (drive, path) = os.path.splitdrive(somepath)
    while 1:
        (path, directory) = os.path.split(path)
        if not directory:
            break
    return drive + path

def print_file_from(filename, pos):
    """ Determine where to start printing from within a file
    """
    with open(filename, 'rb') as fh:
        fh.seek(pos)
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            sys.stdout.write(chunk)

def _fstat(filename):
    """ stat the file
    """
    st_results = os.stat(filename)
    return (st_results[6], st_results[8])

def _print_if_needed(filename, last_stats):
    changed = False
    #Find the size of the file and move to the end
    tup = _fstat(filename)
    if last_stats[filename] != tup:
        changed = True
        print_file_from(filename, last_stats[filename][0])
        last_stats[filename] = tup
    return changed

def multi_tail(filenames, stdout=sys.stdout, interval=1, idle=10):
    S = lambda (st_size, st_mtime): (max(0, st_size - 124), st_mtime)
    last_stats = dict((fn, S(_fstat(fn))) for fn in filenames)
    last_print = 0
    while 1:
        changed = False
        for filename in filenames:
            if _print_if_needed(filename, last_stats):
                changed = True
        if changed:
            if idle > 0:
                last_print = time.time()
        else:
            if idle > 0 and last_print is not None:
                if time.time() - last_print >= idle:
                    last_print = None
            time.sleep(interval)


# Build a path to the logflag file in a platform non-specific way
nxapi_logs_directory = os.path.join(get_root(sys.executable), 'var', 'nginx', 'logs')
nxapi_enable_debug_file = os.path.join(nxapi_logs_directory, "logflag")

# Touch that file so enhanced nxapi debugs start to be logged
touch(nxapi_enable_debug_file)

print "Tailing the access.log, error.log and the nginx.log, use cntl-c (^C)"
print "to exit."

# Tail the logs
logs = []
logs.append(os.path.join(nxapi_logs_directory, "access.log"))
logs.append(os.path.join(nxapi_logs_directory, "error.log"))
logs.append(os.path.join(nxapi_logs_directory, "nginx.log"))

try:
    multi_tail(logs)
except KeyboardInterrupt:
    pass

# Clean up
try:
    os.remove(nxapi_enable_debug_file)
except:
    pass