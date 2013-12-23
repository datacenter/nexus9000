#!/usr/bin/env Python
#
# Sample code to interact with APIC's REST API _without_ the Python SDK
#
# this code simply POSTs XML at the right URL to create a user in the system
# it can easily be adapted to use any of the other XML examples that are in this folder
# 

import urllib2
import base64

handlers = []
hh = urllib2.HTTPHandler()
hh.set_http_debuglevel(0)
handlers.append(hh)

http_header={"User-Agent" : "Chrome/17.0.963.46",
             "Accept" : "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,text/png,*/*;q=0.5",
             "Accept-Language" : "en-us,en;q=0.5",
             "Accept-Charset" : "ISO-8859-1",
             "Content-type": "application/x-www-form-urlencoded"
            }

def createAuthHeader(username,password):
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    return ('Basic %s' % base64string)

def getAPICCookie(ip_addr, authheader, username, password):
    url = 'http://'+ip_addr+':8000/api/aaaLogin.xml'

    # create 'opener' (OpenerDirector instance)
    opener = urllib2.build_opener(*handlers)
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)

    http_header["Host"]=ip_addr
    xml_string = "<aaaUser name='%s' pwd='%s'/>" % (username, password)
    req = urllib2.Request(url=url, data=xml_string, headers=http_header)

    try:
      response = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print 'Failed to obtain auth cookie: %s' % (e)
      return 0
    else:
      rawcookie=response.info().getheaders('Set-Cookie')
      return rawcookie[0]

def createUser(ip_addr, cookie, username, password, role):
    url = 'http://'+ip_addr+':8000/api/policymgr/mo/uni/userext.xml'
    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)
    http_header["Host"]=ip_addr
    http_header["Cookie"]=cookie

    xml_string="<aaaUser name='" + username + "' phone='' pwd='" + password + "'>  \
                 <aaaUserDomain childAction='' descr='' name='all' rn='userdomain-all' status=''> \
                  <aaaUserRole childAction='' descr='' name='" + role + "' privType='writePriv'/>  \
                 </aaaUserDomain> \
                </aaaUser>" 

    req = urllib2.Request(url=url,data=xml_string,headers=http_header)

    try:
     response = urllib2.urlopen(req)
    except urllib2.URLError, e:
     print "URLLIB2 error:\n  %s\n  URL: %s\n  Reason: %s" % (e, e.url, e.reason)
    else:
     return response


#################
#  MAIN MODULE  #
#################

# First things first: credentials. They should be parsed through sys.argv[] ideally ..
ip="<APIC_IP>"
user="admin"
password="password"

basicauth=createAuthHeader(user, password)
cookie=getAPICCookie(ip, basicauth, user, password)
if cookie:
    print "We have a cookie:\n  %s\n" % cookie
    print "Creating user ..\n"
    r=createUser(ip, cookie, "my_user", "my_password", "admin")
    print r.read()
