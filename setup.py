# Copyright 2014 Cisco Systems
#
# (INSERT LICENSING HERE)

from setuptools import setup, find_packages
from distutils.command.install import install as _install

import sys
import platform

if not sys.version_info[0] == 2:
    print "Sorry, Python 3 is not supported (yet)"
    exit()

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    print "Sorry, Python < 2.6 is not supported"
    exit()

setup(name='nexus9000',
      version='1.0',
      description="Python library for interacting with Cisco Application Centric Infrastructure",
      author="(fill in Cisco authors here), Matt Oswalt",
      author_email="(fill in Cisco authors here), matt@keepingitclassless.net",
      url="https://github.com/datacenter/nexus9000",
      packages=find_packages('.'),
      install_requires=[
                    "setuptools>0.6",
                    "paramiko>=1.7.7.1",
                    "lxml>3.0"
                    ],
      license="(fill in license here)",
      platforms=["Linux; OS X; Windows"],
      keywords=('Cisco', 'ACI', 'Application-Centric Infrastructure', 'NXAPI', 'Nexus 9000'),
      classifiers=[
          'Programming Language :: Python',
          'Topic :: System :: Networking',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )







