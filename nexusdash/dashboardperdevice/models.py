from django.db import models
import datetime


class InterfacesStats(models.Model):
    '''Many-to-one relationship. e.i Many InterfacesStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    Many-to-one relationship exists as this model is sued for plotting a graph
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    int_name = models.CharField(max_length=50)
    int_state = models.CharField(max_length=20, default='')
    int_adminstate = models.CharField(max_length=20, default='')
    int_mtu = models.CharField(max_length=20, default='')
    int_bw = models.CharField(max_length=20, default='')
    int_desc = models.CharField(max_length=1000, default='')
    int_hwdesc = models.CharField(max_length=50, default='')
    int_hwaddr = models.CharField(max_length=20, default='')
    int_ipaddr = models.IPAddressField(max_length=20, default='')
    int_ipmask = models.CharField(max_length=20, default='')
    int_bpsrate_rx = models.CharField(max_length=20, default='')
    int_bpsrate_tx = models.CharField(max_length=20, default='')
    int_loadinterval = models.CharField(max_length=20, default='')
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.int_name
     

class OSInfo(models.Model):
    '''One-to-one relationships. e.i One Host can have only one type of OSInfo 
    # https://docs.djangoproject.com/en/1.4/topics/db/examples/one_to_one/
    
    This gets updated by task poll_osinfo()
    '''
    hostname = models.OneToOneField('hostnames.HostNames', primary_key=True, unique=True)
    polling_timestamp = models.FloatField()
    osdevicename = models.CharField(max_length=100)
    osplatform = models.CharField(max_length=100)
    ostime = models.CharField(max_length=100)
    osuptime = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.osdevicename
    
class CpuStats(models.Model):
    '''Many-to-one relationship. e.i Many CpuStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    This gets updated by task poll_cpustats()
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    per1min = models.CharField(max_length=10)
    per5min = models.CharField(max_length=10)
    per15min = models.CharField(max_length=10)
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.hostname.hostname
    
    
class MemStats(models.Model):
    '''Many-to-one relationship. e.i Many MemStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    This gets updated by task poll_memstats()
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    mem_used = models.CharField(max_length=20)
    mem_free = models.CharField(max_length=20)
    mem_total = models.CharField(max_length=20)
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.hostname.hostname
    
    
class DirStats(models.Model):
    '''Many-to-one relationship. e.i Many DirStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    This gets updated by task poll_dirstats()
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    used = models.CharField(max_length=20)
    free = models.CharField(max_length=20)
    total = models.CharField(max_length=20)
    used_percent = models.CharField(max_length=20)
    module = models.CharField(max_length=20)
    dirpath = models.CharField(max_length=20)
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.hostname.hostname
    
class ModulesStats(models.Model):
    '''Many-to-one relationship. e.i Many ModulesStats for one HostName
    # https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/
    
    This gets updated by task poll_dirstats()
    '''
    hostname = models.ForeignKey('hostnames.HostNames')
    polling_timestamp = models.FloatField()
    status = models.CharField(max_length=20)
    mod_id = models.CharField(max_length=20)    # Module no. or Module Name
    serial_no = models.CharField(max_length=20, default='')
    diag_stat = models.CharField(max_length=20, default='')
    hw_model = models.CharField(max_length=20, default='')
    hw_desc = models.CharField(max_length=100, default='')
    ports = models.CharField(max_length=20, default='')
    
    def __unicode__(self):
        return str(datetime.datetime.fromtimestamp(self.polling_timestamp)) + '-' + self.hostname.hostname
    