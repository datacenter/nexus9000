import sys
sys.path.append('pysdk')
from insieme.mit import access
access.rest()
directory = access.MoDirectory(ip='172.21.128.100', port='8000', user='admin', password='password')
polUni = directory.lookupByDn('uni')
fvTenantMo = directory.create('fv.Tenant', polUni, name='Tenant1')
d = directory.commit(polUni)
