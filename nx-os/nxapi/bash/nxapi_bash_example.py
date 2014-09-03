import requests
import json

"""
Modify these please
"""
url='http://IP_ADDRESS/ins'
switchuser='username'
switchpassword='password'

myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "bash",
    "chunk": "0",
    "sid": "1",
    "input": "cd /bootflash; ls",
    "output_format": "json"
  }
}


response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()

print(response)