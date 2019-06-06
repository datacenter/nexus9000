#  When using NX-API, all exec commands, such as the copy command in the input field below, require the cli_conf option, as shown in the type field below. 

import requests
import json

"""
Modify these please
"""
switchuser='admin'
switchpassword='pass1234'

url='http://<IP_Address>/ins'
myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_conf",
    "chunk": "0",
    "sid": "sid",
    "input": "copy tftp://<IP_Address>//auto/tftp-sjc-users2/<UserName>/Leaf1-running-config bootflash: vrf management",
    "output_format": "json"
  }
}
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

print(response)
