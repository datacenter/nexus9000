# This script demonstrates how to set and enable a certificate and key file through the DME REST API.
# After configuring and enabling the certificate and key, use the show nxapi command to check if the certificate and key installed. 

import requests
import json

"""
Modify these please
"""
switchuser='admin'
switchpassword='pass123'

url='http://<IP_Address/ins'
myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_conf",
    "chunk": "0",
    "sid": "sid",
    "input": "show nxapi",
    "output_format": "json"
  }
}
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

print(response)

userid-M-83HS:NXAPI_IREL userid$ python3 sh_nxapi.py 
{'ins_api': {'sid': 'eoc', 'type': 'cli_conf', 'version': '1.0', 'outputs': {'output': {'body': 'nxapi enabled\nHTTP Listen on port 80\nHTTPS Listen on port 443\nCertificate Information:\n    Issuer:   /C=US/ST=CA/L=San Jose/O=Cisco Systems Inc./OU=dcnxos/CN=nxos\n    Expires:  Apr 26 22:19:06 2019 GMT                                         \n', 'code': '200', 'msg': 'Success'}}}}
userid-M-83HS:NXAPI_IREL userid$ 
