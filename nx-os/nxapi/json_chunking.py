# Makes multiple requests in line with JSON formatting.

import requests
import json
import os
import multiprocessing
import time
import ssl
import re
import threading

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
from requests.packages.urllib3.exceptions import SNIMissingWarning

requests.packages.urllib3.disable_warnings(SNIMissingWarning)


url = 'https://{ip address}/ins'
switchuser = 'usermame'
switchpassword = 'password'

def aRequest():
    sid = "sid"

    filename = "show_ip_static_route.json"

    if os.path.isfile(filename):
        os.remove(filename)

    while sid != "eoc":

        r = requests.get(url, auth=(switchuser, switchpassword), verify=False)
        cookies = r.cookies
        cookieDict = cookies.get_dict()
        cookieAuth = cookieDict.get('nxapi_auth')
        myheaders = {'content-type': 'application/json', "Cookie": "nxapi_auth=" + cookieAuth}

        payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "1",
                "sid": "%s" % sid,
                "input": "show ip static-route",
                "output_format": "json"
            }
        }


        response = requests.post(url, data=json.dumps(payload), headers=myheaders, verify=False)
        out = response.content.decode('utf-8')

        regex = '.*\"sid\": *\"(.*)\",\"outputs'

        match = re.search(regex, out)

        sid = match.group(1)

        regex_body = '.*\"body\": *(.*)'

        match = re.search(regex_body, out)

        body = match.group(1)

        outFile = open(filename, "a")
        outFile.writelines(body)
        outFile.close()

if __name__ == '__main__':
    aRequest()

