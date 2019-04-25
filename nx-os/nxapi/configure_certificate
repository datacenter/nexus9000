import json
import requests
import ssl
import time

"""
Modify these please
"""
username = "admin"
password = "pass1234"



ip_addr =  "<IP_Address>"
endpoints = "/api/mo/sys.json"
payload = {
  "topSystem": {
    "children": [
      {
        "nxapiInst": {
          "attributes": {
            "certEnable": "yes",
            "certFile": "bootflash:/server.crt.new",
            "keyFile": "bootflash:/server.key.new"
          }
        }
      }
    ]
  }
}


def aaa_login(username, password, ip_addr):
    payload = {
        'aaaUser' : {
            'attributes' : {
                'name' : username,
                'pwd' : password
                }
            }
        }
    url = "http://" + ip_addr + "/api/aaaLogin.json"
    auth_cookie = {}

    response = requests.request("POST", url, data=json.dumps(payload))
    if response.status_code == requests.codes.ok:
        data = json.loads(response.text)['imdata'][0]
        token = str(data['aaaLogin']['attributes']['token'])
        auth_cookie = {"APIC-cookie" : token}

    print ()
    print ("aaaLogin RESPONSE:")
    print (json.dumps(json.loads(response.text), indent=2))

    return response.status_code, auth_cookie


def aaa_logout(username, ip_addr, auth_cookie):
    payload = {
        'aaaUser' : {
            'attributes' : {
                'name' : username
                }
            }
        }
    url = "http://" + ip_addr + "/api/aaaLogout.json"

    response = requests.request("POST", url, data=json.dumps(payload),
                                cookies=auth_cookie)

    print ()
    print ("aaaLogout RESPONSE:")
    print (json.dumps(json.loads(response.text), indent=2))
    print ()


def post(ip_addr, auth_cookie, url, payload):
    response = requests.request("POST", url, data=json.dumps(payload),
                                cookies=auth_cookie)

    print ()
    print ("POST RESPONSE:")
    print (json.dumps(json.loads(response.text), indent=2))


if __name__ == '__main__':
    status, auth_cookie = aaa_login(username, password, ip_addr)
    if status == requests.codes.ok:
        url = "http://" + ip_addr + endpoints 
        post(ip_addr, auth_cookie, url, payload)
        aaa_logout(username, ip_addr, auth_cookie)
        time.sleep(10)
        url='http://<IP_Address>/ins'
        myheaders={'content-type':'application/json'}
        payload={
        "ins_api": {
        "version": "1.0",
        "type": "cli_show",
        "chunk": "0",
        "sid": "sid",
        "input": "show nxapi",
        "output_format": "json"
        }
        }
        response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(username,password)).json()
        print(response)
