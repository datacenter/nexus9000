from __future__ import absolute_import

from celery import shared_task
from hostnames.models import HostNames
from .models import OSInfo
from .models import InterfacesStats
from .models import CpuStats
from .models import MemStats
from .models import DirStats
from .models import ModulesStats
from utils.fetchcliout import fetchcli_wrapper
import time

@shared_task
def poll_osinfo(hostname):
    '''
    Create only one entry for any no. of polls
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    d = fetcho.get_osinfo()
    osdevicename = d['osdevicename']
    osplatform = d['osplatform']
    ostime = d['ostime']
    osuptime = d['osuptime']
    if len(OSInfo.objects.filter(hostname=hostname_obj)) == 0:
        o = OSInfo(hostname=hostname_obj, polling_timestamp=time.time(),
               osdevicename=osdevicename, osplatform=osplatform,
               ostime=ostime, osuptime=osuptime)
    else:
        o = OSInfo.objects.get(hostname=hostname_obj)
        o.polling_timestamp = time.time()
        o.osdevicename = osdevicename
        o.osplatform = osplatform
        o.ostime = ostime
        o.osuptime = osuptime
    o.save()


@shared_task
def poll_cpustats(hostname):
    '''
    Create new entry for every poll
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    d = fetcho.get_cpustats()
    o = CpuStats(hostname=hostname_obj, polling_timestamp=time.time(), **d)
    o.save()

@shared_task
def poll_memstats(hostname):
    '''
    Create new entry for every poll
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    d = fetcho.get_memstats()
    o = MemStats(hostname=hostname_obj, polling_timestamp=time.time(), **d)
    o.save()
    
@shared_task
def poll_intstats(hostname=None):
    '''
    Create new entry for every poll
    @param hostname: Hostname. If == None, then run for all hostnames
    '''
    if hostname == None:
        for h in HostNames.objects.all():
            _poll_intstats(h.hostname)
    else:
        _poll_intstats(hostname)
            
def _poll_intstats(hostname):
    '''
    This is done in order to allow polling of intstats
    periodically for all hostnames
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    list_of_ints = fetcho.get_intstats()
    timestamp = time.time()         # Using one common timestamp for one query to device
    for d in list_of_ints:
        o = InterfacesStats(hostname=hostname_obj,
                             polling_timestamp=timestamp,
                             **d)
        o.save()
        
@shared_task
def poll_dirstats(hostname):
    '''
    Create new entry for every poll
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    list_of_modules = fetcho.get_dirstats()
    timestamp = time.time()         # Using one common timestamp for one query to device
    for d in list_of_modules:
        o = DirStats(hostname=hostname_obj,
                             polling_timestamp=timestamp,
                             **d)
        o.save()
        
@shared_task
def poll_modulestats(hostname):
    '''
    Create new entry for every poll
    '''
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.save()
    list_of_modules = fetcho.get_modulestats()
    timestamp = time.time()         # Using one common timestamp for one query to device
    for d in list_of_modules:
        o = ModulesStats(hostname=hostname_obj,
                             polling_timestamp=timestamp,
                             **d)
        o.save()
        