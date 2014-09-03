import requests
import json

"""
Modify these please
"""
url='http://10.201.30.194/ins'
switchuser='ewibowo'
switchpassword='Maryani75'

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