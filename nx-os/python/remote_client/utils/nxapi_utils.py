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

import urllib2

import contextlib
import base64

import socket

import httplib
from httplib import HTTPConnection, HTTPS_PORT
import ssl

from lxml import etree

class HTTPSConnection(HTTPConnection):
    "This class allows communication via SSL."
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
            strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
            source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock,
                                    self.key_file,
                                    self.cert_file,
                                    ssl_version=ssl.PROTOCOL_SSLv3)

httplib.HTTPSConnection = HTTPSConnection

class RequestMsg:
    def __init__(self, msg_type="cli_show", ver="0.1", sid="1", 
                input_cmd="show version", out_format="json", do_chunk="0"):
        self.msg_type = msg_type
        self.ver = ver
        self.sid = sid
        self.input_cmd = input_cmd
        self.out_format = out_format
        self.do_chunk = do_chunk

    def get_req_msg_str(self, msg_type="cli_show", ver="0.1", sid="1", 
                input_cmd="show version", out_format="json", do_chunk="0"):
        req_msg = "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"
        req_msg += "<ins_api>\n"
        req_msg += "<type>"+msg_type+"</type>\n"
        req_msg += "<version>"+ver+"</version>\n"
        req_msg += "<chunk>"+do_chunk+"</chunk>\n"
        req_msg += "<sid>"+sid+"</sid>\n"
        req_msg += "<input>"+input_cmd+"</input>\n"
        req_msg += "<output_format>"+out_format+"</output_format>\n"
        req_msg += "</ins_api>\n"
        return req_msg

class RespFetcher:
    def __init__(self, username="admin", password="insieme", 
                 url="http://172.21.128.227/ins"):
        self.username = username
        self.password = password
        self.url = url
        self.base64_str = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

    def get_resp(self, req_str, cookie, timeout):
        req = urllib2.Request(self.url, req_str)
        req.add_header("Authorization", "Basic %s" % self.base64_str)
        req.add_header("Cookie", "%s" % cookie)
        try:
            with contextlib.closing(urllib2.urlopen(req, timeout=timeout)) as resp:
                resp_str = resp.read()
                resp_headers = resp.info()
                return resp_headers, resp_str
        except socket.timeout, e:
            print "Req timeout"
            raise

class RespFetcherHttps:
    def __init__(self, username="admin", password="insieme", 
                 url="https://172.21.128.227/ins"):
        self.username = username
        self.password = password
        self.url = url
        self.base64_str = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

    def get_resp(self, req_str, cookie, timeout):
        req = urllib2.Request(self.url, req_str)
        req.add_header("Authorization", "Basic %s" % self.base64_str)
        req.add_header("Cookie", "%s" % cookie)
        try:
            with contextlib.closing(urllib2.urlopen(req, timeout=timeout)) as resp:
                resp_str = resp.read()
                resp_headers = resp.info()
                return resp_headers, resp_str
        except socket.timeout, e:
            print "Req timeout"
            raise

class NXAPI:
    target_url = ""
    username = ""
    password = ""

    timeout = 10

    out_format = "xml"
    do_chunk = "0"
    sid = "sid"
    cookie = "no-cookie"

    req_obj = RequestMsg()
    @staticmethod
    def init(target_url, username, password):
        NXAPI.target_url = target_url
        NXAPI.username = username
        NXAPI.password = password
        NXAPI.req_fetcher = RespFetcher(username=username,
                                        password=password,
                                        url=target_url)
    
    @staticmethod 
    def send_cmd(cmd, msg_type):
        req_msg_str = NXAPI.req_obj.get_req_msg_str(msg_type=msg_type,
                                                    input_cmd=cmd, 
                                                    out_format=NXAPI.out_format,
                                                    do_chunk=NXAPI.do_chunk,
                                                    sid=NXAPI.sid)
        resp_headers, resp_str = NXAPI.req_fetcher.get_resp(req_msg_str,
                                                      NXAPI.cookie,
                                                      NXAPI.timeout)
        if "Set-Cookie" in resp_headers:
            NXAPI.cookie = resp_headers["Set-Cookie"]
        content_type = resp_headers["Content-Type"]
        root = etree.fromstring(resp_str)
        body = root.findall(".//body")
        code = root.findall(".//code")
        msg  = root.findall(".//msg")

        output = None
        if len(body) != 0:
            if msg_type == 'cli_show':
                output = etree.tostring(body[0])
            else:
                output = body[0].text

        return [output, code[0].text, msg[0].text]