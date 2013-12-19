## NX-API Authentication with [Splunk's REST API Modular Input App](http://apps.splunk.com/app/1546/)

The NX-API authentication process can be described as follows:

 * All requests should include HTTP Web Basic Authentication - that includes requets that also have a cookie.
 * A request that does not have a cookie but does have HTTP Web Basic Authentication will cause the NX-API enabled device to go through a full authentication process using the PAM.  This is an expensive process for a network element (switch) so it should be avoided if possible.
 * Once the authentication is completed a cookie with the key `nxapi_auth` will be generated and included in the headers of the response.
 * When the client receives the response, the client should then send all requests with both HTTP Web Basic Authentication **AND** `nxapi_auth` the cookie.
 * If the NX-API enabled device sends a new cookie for any reason the client must be able to deal with that and be able to send the new cookie from that point forward.

### nx-api_authhandlers.py

nx-api_authhandlers.py - a custom authentication handler for Cisco's NX-API
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

```param username``` The username used to authenticate the user.<br />
```param password``` The password used to authenticate the user.<br />
```param name``` A unique name for the Rest API action configured as a
    data input, the common practice is to set this to the "Rest API
    Input Name" and this must match the name from the "Response
    Handler Arguments" configuration.

    This custom authentication handler should be merged into:
        rest_ta/bin/authhandlers.py

    Tested with Splunk version 6.0 & Rest API Modular Input v1.3.2

### nx-api_responsehandlers.py

nx-api_responsehandlers.py - a custom response handler for Cisco's NX-API
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
    name=\<ame> 

Where:

```name``` A unique name for the Rest API action configured as a data input, the common practice is to set this to the "Rest API Input Name" and this must match the name from the "Custom Authentication Handler Arguments" configuration. 

This response handler should be merged into:
    rest_ta/bin/responsehandlers.py

Tested with Splunk version 6.0 & Rest API Modular Input v1.3.2
    
### debugging issues with this code

The only way I have found to get debugging output from Splunk and the [REST API Modular Input](http://apps.splunk.com/app/1546/) code is to set things up as follows:

 * Add the following to rest_ta/bin/rest.py and comment out the other logging code:
 ```python
 import logging
 logging.basicConfig() 
 logging.getLogger().setLevel(logging.DEBUG)
 requests_log = logging.getLogger("requests.packages.urllib3")
 requests_log.setLevel(logging.DEBUG)
 requests_log.propagate = True
 ```
 * Add the following to rest_ta/bin/authhanders.py and/or rest_ta/bin/responsehandlers.py:
 ```python
 #set up logging
 import logging
 logging.root
 logging.root.setLevel(logging.DEBUG)
 formatter = logging.Formatter('%(levelname)s %(message)s')
 #with zero args , should go to STD ERR
 handler = logging.StreamHandler()
 handler.setFormatter(formatter)
 logging.root.addHandler(handler)
 ```
 * Litter the code with:
 ```python
 logging.debug("This is a debug {0}".format("message")
 ```
 * Enable debug logging in Splunk system settings - (Splunk 6) Settings -> System -> System Settings -> System logging.  Search for ExecProcessor and change it to Debug.
 * Restart the Splunk server - Settings -> System -> Server controls: Restart Splunk
 * If you need to get more info out of exceptions you can import the traceback module into rest.py and print a traceback where `except Exception as e:` is used.

