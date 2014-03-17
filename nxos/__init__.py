# Copyright 2014 Cisco Systems
#
# (INSERT LICENSING HERE)

__version__ = (1,0)

import sys

if sys.version_info < (2, 6):
    raise RuntimeError('You need Python 2.6+ for this module.')

class nexus9000ClientError(Exception):
    "Base type for all nexus9000 errors"
    pass
