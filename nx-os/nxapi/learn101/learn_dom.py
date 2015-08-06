import os
import sys
import subprocess
import base64,xml.dom.minidom
from xml.dom.minidom import Node
f = open("file.xml",'r')
data = f.read()
i = 0
doc = xml.dom.minidom.parseString(data)
titles = doc.getElementsByTagName('Title')

for title in doc.getElementsByTagName('Title'):
    print(title.firstChild.nodeValue)

#for i in range(0,len(titles)):
#    print(titles[i].firstChild.nodeValue)

