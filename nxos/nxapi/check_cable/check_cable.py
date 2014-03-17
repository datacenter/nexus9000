
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

import time

import urllib
import urllib2

import json
import contextlib
import threading
import base64

import sys
import socket

sys.path.append("../utils")

from nxapi_utils import NXAPI

def get_connectivity(url, method="cdp"):
    nxapi = NXAPI()
    nxapi.set_target_url(url)
    nxapi.set_username("admin")
    nxapi.set_password("insieme")
    nxapi.set_msg_type("cli_show")
    nxapi.set_out_format("json")
    nxapi.set_cmd("show switchname")
    headers, resp = nxapi.send_req()
    resp_obj = json.loads(resp)

    switchname = resp_obj["ins_api"]["outputs"]["output"]["body"]["hostname"]
    if method == "cdp":
        nxapi.set_cmd("show cdp neighbor")
        headers, resp = nxapi.send_req()
        resp_obj = json.loads(resp)

        neighbors = resp_obj["ins_api"]["outputs"]["output"]["body"]["TABLE_cdp_neighbor_brief_info"]["ROW_cdp_neighbor_brief_info"]
        connectivity_list = list()
        for i in range (0, len(neighbors)):
            remote_switch = neighbors[i]["device_id"]
            index = remote_switch.find("(")
            if index != -1:
                remote_switch = remote_switch[0:index]
            one_neighbor = '{0};{1};{2};{3}'.format(switchname, 
                                                   neighbors[i]["intf_id"],
                                                   remote_switch,
                                                   neighbors[i]["port_id"])
            connectivity_list.append(one_neighbor)
    else:
        nxapi.set_cmd("show lldp neighbor")
        headers, resp = nxapi.send_req()
        resp_obj = json.loads(resp)

        neighbors = resp_obj["ins_api"]["outputs"]["output"]["body"]["TABLE_nbor"]["ROW_nbor"]
        connectivity_list = list()
        for i in range (0, len(neighbors)):
            remote_switch = neighbors[i]["chassis_id"]
            index = remote_switch.find("(")
            if index != -1:
                remote_switch = remote_switch[0:index]
            one_neighbor = '{0};{1};{2};{3}'.format(switchname, 
                                                   neighbors[i]["l_port_id"],
                                                   remote_switch,
                                                   neighbors[i]["port_id"])
            connectivity_list.append(one_neighbor)
    return connectivity_list


def do_work(switches, blueprint, method):

    connectivities = list()
    for i in range(0, len(switches)):
        connectivities.append(get_connectivity(switches[i], method))

    print "######################## Connectivity BEGIN #############################"
    for i in range(0, len(connectivities)):
        print "******************************************************************"
        for j in range(0, len(connectivities[i])):
            items = connectivities[i][j].split(";")
            print "[" + items[0] + "]:" + items[1] + " ------> [" + items[2] + "]:" + items[3]
    print ""
    print "######################## Bidirection Check Result #######################"
    for i in range(0, len(connectivities)):
        conn1 = connectivities[i]
        for j in range(i + 1, len(connectivities)):
            conn2 = connectivities[j]
            for k in range(0, len(conn1)):
                items1 = conn1[k].split(";")
                for l in range(0, len(conn2)):
                    items2 = conn2[l].split(";")
                    if items1[0] == items2[2] and items1[1] == items2[3]:
                        print "[" + items1[0] + "]:" + items1[1] + " ---> [" + items1[2] + "]:" + items1[3] + " Connected!"
    print ""
    print "######################## DB Conformance Check Result #####################"
    conn_db = ""
    with open(blueprint, 'r') as content_file:
        conn_db = content_file.read()
    conn_obj = json.loads(conn_db)
    conn_db_list = list()
    nes = conn_obj["ne"]
    for i in range(0, len(nes)):
        ne_name = conn_obj["ne"][i]["name"]
        conns = conn_obj["ne"][i]["connectivity"]
        for j in range(0, len(conns)):
            conn = '{0};{1};{2};{3}'.format(ne_name,
                                              conn_obj["ne"][i]["connectivity"][j]["local_ifx"],
                                              conn_obj["ne"][i]["connectivity"][j]["remote_ne"],
                                              conn_obj["ne"][i]["connectivity"][j]["remote_ifx"])
            conn_db_list.append(conn)
    match_set = set()

    for i in range(0, len(conn_db_list)):
        for j in range(0, len(connectivities)):
            for k in range(0, len(connectivities[j])):
                if method == "lldp":
                    conn_db_list[i] = conn_db_list[i].replace("Ethernet", "Eth")
                if conn_db_list[i] == connectivities[j][k]:
                    items = connectivities[j][k].split(";")
                    print "[" + items[0] + "]:" + items[1] + " ------> [" + items[2] + "]:" + items[3] + " Check Done!"
                    match_set.add(i)

    for i in range(0, len(conn_db_list)):
        if i in match_set:
            continue
        items = conn_db_list[i].split(";")
        print "[" + items[0] + "]:" + items[1] + " ------> [" + items[2] + "]:" + items[3] + " Check Failed!"


# Example: python check_cable.py 10.30.14.11 connectivity.json cdp
if __name__ == "__main__":
    switches = list()
    for i in range(1, len(sys.argv)-2):
        switches.append('http://{0}/ins'.format(sys.argv[i]))
    blueprint = sys.argv[len(sys.argv)-2]
    method = sys.argv[len(sys.argv)-1]
    do_work(switches, blueprint, method)
    
