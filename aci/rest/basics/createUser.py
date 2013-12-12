#!/usr/bin/env Python
#
# Sample code to interact with APIC _without_ the Python SDK
#

import urllib2
import base64
from xml.dom import minidom

handlers = []
hh = urllib2.HTTPHandler()
hh.set_http_debuglevel(0)
handlers.append(hh)

def createAuthHeader(username,password):
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    return ("Basic %s" % base64string)

def getAPICCookie(ip_addr, authheader, username, password):
    url = 'http://'+ip_addr+':8000/api/aaaLogin.xml'

    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(*handlers)
    opener.addheaders = [('Authorization', authheader),]
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)

    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = urllib2.Request(url=url, data=xml_string,)

    try:
      response = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print "Failed to obtain auth cookie: %s" % (e)
      return 0
    else:
      rawcookie=response.info().getheaders('Set-Cookie')
      return rawcookie[0]

	
def createUser(ip_addr, cookie, authheader, username, password, role):
    url = 'http://'+ip_addr+':8000/api/policymgr/mo/uni/userext.xml'
    opener = urllib2.build_opener(*handlers)
    opener.addheaders = [('Cookie', cookie),]
    urllib2.install_opener(opener)

    xml_string="<aaaUser name='" + username + "' phone='' pwd='" + password + "'>  \
		 <aaaUserDomain childAction='' descr='' name='all' rn='userdomain-all' status=''> \
		  <aaaUserRole childAction='' descr='' name='" + role + "' privType='writePriv'/>  \
		 </aaaUserDomain> \
		</aaaUser>" 

    req = urllib2.Request(url=url,
                           data=xml_string,
                           headers={'Authorization': authheader})

    try:
     response = urllib2.urlopen(req)
    except urllib2.URLError, e:
     print e
    else:
     return response


#################
#  MAIN MODULE  #
#################

# First things first: credentials. They should be parsed through sys.argv[] ideally ..
ip="<your_ip>"
user="admin"
password="<your_password>"

basicauth=createAuthHeader(user, password)
cookie=getAPICCookie(ip, basicauth, user, password)
if cookie:
    dom = minidom.parse(createUser(ip, cookie, basicauth, "my_user", "my_password", "admin"))
