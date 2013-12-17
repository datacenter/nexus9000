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
""" nx-api_responsehandlers.py - a custom response handler for Cisco's NX-API
    to handle the nxapi_auth cookie to ensure that the cookie is saved from
    the response so it can be persisted to the next request.  Must be used in
    conjunction with a custom authentication handler that then retrieves the
    cookie and sends it.

    This is accomplished by saving the cookie in a cookie file in the
    (hopefully) platform agnostic way using the tempfile module to do a 
    tempfile.gettempdir() then create or overwrite a file in that directory
    that is specifically named the same as the REST API action configured on
    the splunk server.

    The required custom response handler configuration in the Rest API action
    data input is as follows:

        Custom Response Handler: NxApiResponseHandler
        Custom Authentication Handler Arguments:
           name=<name> 

     Where:

         :param name: A unique name for the Rest API action configured as a
             data input, the common practice is to set this to the "Rest API
             Input Name" and this must match the name from the "Custom
             Authentication Handler Arguments" configuration. 

    This response handler should be merged into:
        rest_ta/bin/responsehandlers.py

    Tested with Splunk version 6.0 & Rest API Modular Input v1.3.2

"""
import os
import pickle
import tempfile

class NxApiResponseHandler:
    """ NxApiResponseHandler simply looks for a nxapi_auth cookie in the
        response from nxapi enabled device and overwrites any existing
        file in the temporary directory with the same filename of "name"
        where name is the name of the Rest API action that is running on
        the splunk server.

        In order for this to work completely there has to be a
        corresponding custom authentication handler that then utilizes that
        saved cookie.

        :param name: The name Rest API input name that uniquely identifies
            the REST API input configuration, this must match the name
            parameter on the corresponding custom response handler.
    """
    COOKIENAME = "nxapi_auth"
    def __init__(self, name, **args):
        self.cookiefilename = self._get_cookiefilename(name)

    def __call__(self, response_object, raw_response_output, response_type,
                 req_args, endpoint):
        """ This gets called when the response is received by this Rest API
            input.  It simply looks for the approriate cookie in the response
            and if one is found it unconditionally tries to unlink the old
            cookie file and save the cookie under a new file.
        """
        if self.COOKIENAME in response_object.cookies:
            try: os.unlink(self.cookiefilename)
            except: pass
            self._save_cookie(response_object.cookies)

    def _get_cookiefilename(self, cookiefilename):
        """ Obtains the absolute path for the cookie filename.  

            :param cookiefile: The unique name for the file that should exist
                in the temporary directory
        """
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, cookiefilename)
        return filename
        
    def _save_cookie(self, r_cookies):
        """" Write the cookie out to the file """
        with open(self.cookiefilename, "wb") as cookiefile:
            pickle.dump(r_cookies, cookiefile)
            cookiefile.flush()

