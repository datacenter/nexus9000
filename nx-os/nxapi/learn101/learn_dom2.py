import os
import sys
import subprocess
import base64,xml.dom.minidom
from xml.dom.minidom import Node
f = open("file2.xml",'r')
data = f.read()
i = 0
doc = xml.dom.minidom.parseString(data)

for title in doc.getElementsByTagName('modinf'):
    print(title.firstChild.nodeValue)

#titles = doc.getElementsByTagName('Title')
#for i in range(0,len(titles)):
#    print(titles[i].firstChild.nodeValue)



