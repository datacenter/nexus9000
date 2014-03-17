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
""" nx-api_authhandlers.py - a custom authentication handler for Cisco's NX-API
    to handle the nxapi_auth cookie to ensure that the cookie is loaded from a 
    file and sent in a request so that basic authentication is not needed again.
    Must be used in conjunction with a custom response handler that then
    receives the the cookie in the response and saves it to the file.

    This is accomplished by the response handler saving the cookie in a cookie
    file in the (hopefully) platform agnostic way using the tempfile module to
    do a tempfile.gettempdir() to find the directory and the file should be
    specifically named the same as the REST API action configured on the splunk
    server.

    The required custom authentication handler configuration in the Rest API
    action data input is as follows:

        Custom Authentication Handler: NxApiAuthHandler
        Custom Authentication Handler Arguments:
            username=<username>,password=<password>,name=<name>

     Where:

         :param username: The username used to authenticate the user.
         :param password: The password used to authenticate the user.
         :param name: A unique name for the Rest API action configured as a
             data input, the common practice is to set this to the "Rest API
             Input Name" and this must match the name from the "Response
             Handler Arguments" configuration.A

    This custom authentication handler should be merged into:
        rest_ta/bin/authhandlers.py

    Tested with Splunk version 6.0 & Rest API Modular Input v1.3.2
"""
import os
from requests.auth import AuthBase
from base64 import b64encode
import pickle
import tempfile

class NxApiAuthHandler(AuthBase):
    """ The basic framework for NxApiAuthHandler comes straight from the
        Requests module HTTPBasicAuth class.  We add the NX-API specific cookie
        handling.  The basic idea is that this custom authentication handler
        will, try to read the cookie from a temporary file.  If no file is
        found then it simply sends the basic auth.  If a cookie is found, 
        then the request is sent with the basic auth + the cookie in the
        headear as NX-API requires.

        In order for this to work, a custom response handler has to also 
        be added.  On the response, the custom response handler will store
        the nxapi_auth cookie provided by the NX-API enabled switch to the
        file so that the custom authentication handler can do its job.

        :param username: The username to be sent to the NX-API enabled switch
        :param password: The password to be sent to the NX-API enabled switch
        :param name: The name Rest API input name that uniquely identifies
            the REST API input configuration, this must match the name
            parameter on the corresponding custom response handler.

        There has to be a corresponding custom response handler as well.
    """
    COOKIENAME = "nxapi_auth"
    def __init__(self, username, password, name):
        self.username = username
        self.password = password
        self.cookiefilename = self._get_cookiefilename(name)
        self.cookiejar = []
        self._update_cookiejar(name)

    def __call__(self, r):
        """ This gets called when a REST action is called.
            This retrieves the nxapi_auth cookie and adds it to the headers
            along with the authorization cookie.

            :param r: the request object
        """
        auth_str = self._basic_auth_str(self.username, self.password)
        r.headers['Authorization'] = auth_str
        self._update_cookiejar(self.cookiefilename)
        if "nxapi_auth" in self.cookiejar:
            r.headers['Cookie'] = self.COOKIENAME + "={0}".format(
                self.cookiejar[self.COOKIENAME])
        return r

    def _basic_auth_str(self, username, password):
        """ Returns a Basic Auth string, in base64 format. """
        return 'Basic ' + b64encode(('%s:%s' % (username,
            password)).encode('latin1')).strip().decode('latin1')

    def _update_cookiejar(self, cookiefilename):
        """ Updates the cookiejar attribute with the latest cookie from the
            cookiefile

            :param cookiefilename: The unique name for the file that should exist
                in the temporary directory
        """
        self.cookiefilename = self._get_cookiefilename(cookiefilename)
        if self.cookiefilename is not None:
            self.cookiejar = self._load_cookies(self.cookiefilename)
        else:
            self.cookiejar = []

    def _get_cookiefilename(self, cookiefilename):
        """ Obtains the absolute path for the cookie filename.  
            
            :param cookiefile: The unique name for the file that should exist
                in the temporary directory
        """
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, cookiefilename or "")
        if os.path.isfile(filename):
            return filename
        else:
            return None

    def _load_cookies(self, filename):
        """ Load in cookies from a file

            :param filename: The file where the cookie is stored
        """
        with open(filename, 'rb') as f:
            return pickle.load(f)
