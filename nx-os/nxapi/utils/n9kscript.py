from nxapi_utils import *

thisNXAPI = NXAPI()
thisNXAPI.set_target_url('http://10.2.1.8/ins')
thisNXAPI.set_username('admin')
thisNXAPI.set_password('Cisco.com')
thisNXAPI.set_msg_type('cli_show')
thisNXAPI.set_cmd('show ip route')
returnData = thisNXAPI.send_req()
#print returnData[1]

doc = xmltodict.parse(returnData[1])

docsub = doc['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']

#for k ,v in doc['ins_api']['outputs']['output']['body']['TABLE_vrf']['ROW_vrf']['TABLE_addrf']['ROW_addrf']['TABLE_prefix'].keys():
#        print k, v
