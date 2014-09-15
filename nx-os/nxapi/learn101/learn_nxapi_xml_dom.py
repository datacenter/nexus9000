import base64
from xml.dom import minidom
import urllib2
import getpass

username='CEC_User'
password=getpass.getpass()
ip_addr='10.201.30.194'

base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
authheader = ("Basic %s" % base64string)

# DEBUG
print("DEBUG1: " + authheader)

handlers = []
hh = urllib2.HTTPHandler()
hh.set_http_debuglevel(0)
handlers.append(hh)

opener = urllib2.build_opener(*handlers)
opener.addheaders = [('Authorization', authheader),]
urllib2.install_opener(opener)

xml_string="<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?> \
<ins_api>                         \
<version>0.1</version>            \
<type>cli_show</type>             \
<chunk>0</chunk>                  \
<sid>session1</sid>               \
<input>show clock</input>         \
<output_format>xml</output_format>\
</ins_api>"

url = 'http://'+ip_addr+'/ins/'
req = urllib2.Request(url=url, data=xml_string,)

try:
      response = urllib2.urlopen(req)
except urllib2.URLError, e:
      print e.code
      print e.read()
else:
      rawcookie=response.info().getheaders('Set-Cookie')
      print("DEBUG2: " + str(rawcookie))

opener = urllib2.build_opener(*handlers)
opener.addheaders = [('Cookie', rawcookie),]
urllib2.install_opener(opener)

xml_string="<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?> \
     <ins_api>                          \
     <version>0.1</version>             \
     <type>cli_show</type>      \
     <chunk>0</chunk>                   \
     <sid>session1</sid>                \
     <input>show cdp neighbor</input>         \
     <output_format>xml</output_format> \
     </ins_api>"

req = urllib2.Request(url=url, data=xml_string, headers={'Authorization': authheader})

try:
    response = urllib2.urlopen(req)
    doc = minidom.parse(response)
except urllib2.URLError, e:
    print e.code
    print e.read()


#f = open("file2.xml",'r')
#data = f.read()
#i = 0
#doc = xml.dom.minidom.parseString(data)

for title in doc.getElementsByTagName('device_id'):
    print(title.firstChild.nodeValue)

#titles = doc.getElementsByTagName('Title')
#for i in range(0,len(titles)):
#    print(titles[i].firstChild.nodeValue)



