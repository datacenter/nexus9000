from __future__ import absolute_import

from celery import shared_task

from utils.fetchcliout import fetchcli_wrapper

@shared_task
def poll_healthinfo(hostname):
    '''
    Try connecting to the device and do initial health check
    Save hostname entry in HostNames table
    
    @param hostname: hostname being submitted by post request to add a new device by user
    '''
    # The provided input has already been saved by form submission LoginForm.save()
    # Updating the entry now...
    hostname_obj, fetcho = fetchcli_wrapper(hostname)
    hostname_obj.is_healthy = fetcho.is_healthy
    hostname_obj.is_online = fetcho.is_online
    hostname_obj.os_type = fetcho.sw_version
    hostname_obj.error_online = fetcho.error_online
    hostname_obj.health_statuses = fetcho.health_statuses
    hostname_obj.save()
    