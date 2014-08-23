'''
@summary: Methods for common device operation tasks
'''

from nxapi.nxapi_utils import NXAPITransport
from urlparse import urlparse
import time
import json
import os
import re


VERSION_OUT_FRMT = 'CHASSIS: {chassis}; IMAGE: {image}'
CPU_THRESHOLD = 50.00
MEMORY_USED_THRESHOLD = 50.00


class FetchCliOut(object):
    def __init__(self, target_url, username, password, **kwargs):
        '''
        @param target_url: URL format. For telnet/ssh use, telnet://hostip:port or ssh://hostip:port
                                       For NXAPI, use http://hostip/ins
        @param username: Username of device
        @param password: Password of device
        '''
        self.username = username
        self.password = password
        self.target_url = target_url
        
        parsed_url = urlparse(target_url)
        self.hostname = parsed_url.hostname
        self.port = parsed_url.port
        
        self.error_online = ''
        self.health_statuses = list()       # Format: [(description, healthy)]
        
        self._is_online = False
        
    def _exception(self, reason):
        raise Exception(reason)
    
    def _log(self, msg):
        print msg

    @property
    def is_healthy(self):
        raise NotImplementedError()
    
    @property    
    def is_online(self):
        raise NotImplementedError()
    
    @property
    def sw_version(self):
        raise NotImplementedError()
        

class FetchViaRoutercli(FetchCliOut):
    '''
    Get output from CLI ssh/telnet as string
    
    TODO: Implement all functions like FetchViaNxapi
    '''
    def __init__(self, *args, **kwargs):
        from utils.routercli.router import Router
        super(FetchViaRoutercli, self).__init__(*args, **kwargs)
        self.routercli_obj = Router(self.hostname, logger=False, logfile_console=None)
        self.routercli_obj.login(username=self.username, password=self.password)
        
    def __del__(self):
        self.routercli_obj.logout()
        

    
class FetchViaNxapi(FetchCliOut):
    '''
    Get output from http/https as JSON
    '''
    def __init__(self, *args, **kwargs):
        super(FetchViaNxapi, self).__init__(*args, **kwargs)
        self.login()
    
    def login(self):
        try:
            NXAPITransport.init(target_url=self.target_url, username=self.username, 
                                password=self.password)
            NXAPITransport.cli('! Testing if device is online')
        except Exception as e:
            self._is_online = False
            e = str(e).lower()
            if 'timed out' in e:
                self.error_online = ('Connection timed out!! Make sure that '
                                     'URL provided ({0}) is accurate'
                                     '').format(self.target_url)
            elif 'unauthorized' in e:
                self.error_online = ('Unauthorized!! Make sure that username '
                                    '({0}) and/or password provided are accurate'
                                    '').format(self.username)
            elif 'target machine actively refused it' in e:
                self.error_online = ('NXAPI TCP Port not open!! Make sure '
                                     '"feature nxapi" is configured on '
                                     'target Nexus switch')
            else:
                self.error_online = e
        else:
            self._is_online = True
        return self._is_online
        
    @property
    def sw_version(self):
        version = ''
        if self._is_online is True:
            version = VERSION_OUT_FRMT
            o = json.loads(NXAPITransport.clid('show version'))
            version = version.format(chassis=o['chassis_id'], 
                                     image=o['kick_file_name'])
        return version
    
    @property
    def is_healthy(self):
        healthy = True
        if self._is_online is True:
            o1 = json.loads(NXAPITransport.clid('show system resources'))
            loads = list()
            loads.append(float(o1['cpu_state_kernel']))
            loads.append(float(o1['load_avg_1min']))
            loads.append(float(o1['load_avg_15min']))
            loads.append(float(o1['cpu_state_user']))
            healthy_cpu = True
            cpu_used_percent = ('{0} (Kernel), {1} (1min), {2} '
                                '(15min), {3} (User)'
                                '').format(loads[0], loads[1], 
                                           loads[2], loads[3])
            for load in loads:
                if load > CPU_THRESHOLD:
                    healthy_cpu = False
                    healthy = False
            loggedin_msg = 'Logged in successfully to {0}'.format(self.target_url)
            self.health_statuses.append((loggedin_msg, True))
            self.health_statuses.append(('CPU Used (%): {0}'.format(cpu_used_percent), 
                                         healthy_cpu))
               
            memory_usage_used = float(o1['memory_usage_used'])
            memory_usage_total = float(o1['memory_usage_total'])
            mem_used_percent = memory_usage_used/memory_usage_total*100
            if mem_used_percent > MEMORY_USED_THRESHOLD:
                healthy_mem = False
                healthy = False
            else:
                healthy_mem = True
            self.health_statuses.append((('Memory Used (%): {0:.2f}'
                                         ''.format(mem_used_percent)), 
                                         healthy_mem))
                
            current_memory_status = o1['current_memory_status']
            if current_memory_status != 'OK':
                healthy_mem_txt = False
                healthy = False
            else:
                healthy_mem_txt = True
            self.health_statuses.append((('Current Memory Status: {0}'
                                         ''.format(current_memory_status)), 
                                         healthy_mem_txt))
            
            o2 = json.loads(NXAPITransport.clid('show module'))
            online_diag_statuses = o2['TABLE_moddiaginfo']['ROW_moddiaginfo']
            diagstatuses = True
            for r in online_diag_statuses:
                diagstatus = r['diagstatus']
                if diagstatus != 'Pass':
                    diagstatuses = False
                    healthy = False
                    self.health_statuses.append((('Module no. {0} '
                                                 'Diag Status: {1}'
                                                 ''.format(r['mod'], diagstatus)), 
                                                 diagstatuses))
            
            if diagstatuses:
                self.health_statuses.append(('Modules Diag Status: Pass', 
                                             diagstatuses))
            
            modinfo = o2['TABLE_modinfo']['ROW_modinfo']
            modstatus = True
            for r in modinfo:
                status = r['status']
                if status not in ['ok', 'active', 'active *', 'standby']:
                    modstatus = False
                    healthy = False
                    self.health_statuses.append((('Module no. {0} Status: {1}'
                                                  ''.format(r['modinf']), status), 
                                                 modstatus))
            
            if modstatus:
                self.health_statuses.append(('Modules Status: Ok', modstatus))
        else:
            healthy = False
        return healthy
    
    @property
    def is_online(self):
        return self.login()
    
    def get_osinfo(self):
        '''
        @return: dict d with keys: 'osdevicename', 'osplatform',
                                    'ostime', 'osuptime'
        '''
        d = {'osdevicename': '',
             'osplatform': '',
             'ostime': '',
             'osuptime': ''}
        if self._is_online:
            version = VERSION_OUT_FRMT
            o = json.loads(NXAPITransport.clid('show version'))
            version = version.format(chassis=o['chassis_id'], 
                                     image=o['kick_file_name'])
            osuptime = ('days: {0}, hrs: {1}, mins: {2}, secs: {3}'
                        ''.format(o['kern_uptm_days'], o['kern_uptm_hrs'],
                                  o['kern_uptm_mins'], o['kern_uptm_secs']))
            devicename = o['host_name']
            o = json.loads(NXAPITransport.clid('show clock'))
            ostime = o["simple_time"]
            d['osplatform'] = version
            d['osdevicename'] = devicename
            d['ostime'] = ostime
            d['osuptime'] = osuptime
        return d
    
    def get_cpustats(self):
        '''
        @return: dict d with keys matching exactly as 
        attributes of dashboardperdevice.models.CpuStats
        '''
        d = dict()
        if self._is_online:
            o = json.loads(NXAPITransport.clid('show system resources'))
            d['per1min'] = o['load_avg_1min']
            d['per5min'] = o['load_avg_5min']
            d['per15min'] = o['load_avg_15min']
        return d
    
    def get_memstats(self):
        '''
        @return: dict d with keys matching exactly as 
        attributes of dashboardperdevice.models.MemStats
        '''
        d = dict()
        if self._is_online:
            o = json.loads(NXAPITransport.clid('show system resources'))
            d['mem_used'] = o['memory_usage_used']
            d['mem_free'] = o['memory_usage_free']
            d['mem_total'] = o['memory_usage_total']
        return d
    
    def get_dirstats(self):
        '''
        @return: dict d with keys matching exactly as 
        attributes of dashboardperdevice.models.DirStats
        '''
        l = list()
        modules_dirs = [['sup-active', 'bootflash'], ['sup-standby', 'bootflash']]
        if self._is_online:
            for module, dirpath in modules_dirs:
                cmd = 'dir {0}://{1}'.format(dirpath, module)
                o = NXAPITransport.cli(cmd)
                d = dict()
                try:
                    d['used'] = re.search('(\d+ bytes) used', o).group(1)
                    d['free'] = re.search('(\d+ bytes) free', o).group(1)
                    d['total'] = re.search('(\d+ bytes) total', o).group(1)
                    
                    used = float(d['used'].rstrip(' bytes'))
                    total = float(d['total'].rstrip(' bytes'))
                    used_percent = (used/total)*100
                    d['used_percent'] = '{0}%'.format(int(used_percent))
                except:
                    d['used'] = d['free'] = d['total'] = d['used_percent'] = 'NA'
                d['module'] = module
                d['dirpath'] = dirpath
                l.append(d)
        return l
    
    def get_modulestats(self):
        '''
        @return: dict d with keys matching exactly as 
        attributes of dashboardperdevice.models.ModulesStats
        '''
        l = list()
        if self._is_online:
            o = json.loads(NXAPITransport.clid('show module'))
            try:
                diaginfos = o['TABLE_moddiaginfo']['ROW_moddiaginfo'] 
                modinfos = o['TABLE_modinfo']['ROW_modinfo']
                modmacinfos = o['TABLE_modmacinfo']['ROW_modmacinfo']
                for r in modinfos:
                    d = dict()
                    d['status'] = r['status']
                    d['hw_desc'] = r['modtype']
                    d['hw_model'] = r['model']
                    d['mod_id'] = r['modinf']
                    d['ports'] = r['ports']
                    d['serial_no'] = [i['serialnum'] for i in modmacinfos if i['modmac'] == d['mod_id']][0]
                    d['diag_stat'] = [i['diagstatus'] for i in diaginfos if i['mod'] == d['mod_id']][0]
                    l.append(d)
            except Exception as e:
                print 'Error while get_modulestats', e
        return l
    
    def get_intstats(self):
        '''
        @return: dict d with keys matching exactly as 
        attributes of dashboardperdevice.models.InterfacesStats
        '''
        list_of_ints = list()
        if self._is_online:
            rows = json.loads(NXAPITransport.clid('show interface'))['TABLE_interface']['ROW_interface']
            for o in rows:
                d = dict()
                int_name = o["interface"]
                d['int_name'] = int_name
                if 'vlan' in int_name.lower():
                    int_state = o.get("svi_line_proto", '')
                    int_adminstate = o.get("svi_admin_state", '')
                    int_mtu = o.get("svi_mtu", '')
                    int_bw = o.get("svi_bw", '')
                    int_hwdesc = o.get("svi_hw_desc", "VLAN")
                    int_hwaddr = o.get("svi_mac", '')
                    int_ipaddr = o.get("svi_ip_addr", '')
                    int_ipmask = o.get("svi_ip_mask", '')
                else:
                    int_state = o.get("state", '')
                    int_adminstate = o.get("admin_state", int_state)
                    int_mtu = o.get("eth_mtu", '')
                    int_bw = o.get("eth_bw", '')
                    int_hwdesc = o.get("eth_hw_desc", '')
                    int_hwaddr = o.get("eth_hw_addr", '')
                    int_ipaddr = o.get("eth_ip_addr", '')
                    int_ipmask = o.get("eth_ip_mask", '')
                if 'mgmt' in int_name.lower():
                    int_bpsrate_rx = o.get("vdc_lvl_in_avg_bits", '')
                    int_bpsrate_tx = o.get("vdc_lvl_out_avg_bits", '')
                    int_loadinterval = 60
                else:
                    int_bpsrate_rx = o.get("eth_inrate1_bits", '')
                    int_bpsrate_tx = o.get("eth_outrate1_bits", '')
                    int_loadinterval = o.get("eth_load_interval1_rx", 0)
                if 'down' in int_state.lower():
                    int_bpsrate_tx = int_bpsrate_rx = 0
                    
                d['int_state'] = int_state
                d['int_adminstate'] = int_adminstate
                d['int_mtu'] = int_mtu
                d['int_bw'] = int_bw
                d['int_desc'] = o.get("desc", '')
                d['int_hwdesc'] = int_hwdesc
                d['int_hwaddr'] = int_hwaddr
                d['int_ipaddr'] = int_ipaddr
                d['int_ipmask'] = int_ipmask
                d['int_bpsrate_rx'] = int_bpsrate_rx
                d['int_bpsrate_tx'] = int_bpsrate_tx
                d['int_loadinterval'] = int(int_loadinterval)
                list_of_ints.append(d)
                
        return list_of_ints
    
def fetchcli_wrapper(hostname):
    '''
    This function is wrapper for getting FetchVia* object and 
    query object for a hostname
    Only two things are modified in the HostNames DB here:
    * timestamp
    * polling_method
    
    The entry of hostname in HostNames is created by a POST to form LoginForm
    '''
    from django.conf import settings
    from hostnames.models import HostNames
    
    hostname_obj = HostNames.objects.get(hostname=hostname)
    hostname_obj.polling_timestamp = time.time()
    
    # Trying to connect
    target_url = hostname_obj.url
    username = hostname_obj.username
    password = HostNames._meta.get_field('password').value_from_object(hostname_obj) # @UndefinedVariable
    
    parsed_url = urlparse(target_url)
    
    if parsed_url.path == '/ins' and 'http' in parsed_url.scheme:
        polling_method = settings.POLLING_METHOD_NXAPI
    else:
        polling_method = settings.POLLING_METHOD_CLI
    hostname_obj.polling_method = polling_method
    
    if polling_method == settings.POLLING_METHOD_CLI:
        fetcho = FetchViaRoutercli(target_url=target_url, username=username, password=password)
    elif polling_method == settings.POLLING_METHOD_NXAPI:
        fetcho = FetchViaNxapi(target_url=target_url, username=username, password=password)
    return hostname_obj, fetcho
    
    
def main():
    pass
#     fetcho = FetchViaRoutercli(target_url='telnet://comcast-term-1', username='cisco', password='cisco')
#     print 'out1', repr(fetcho.get_os_info())
#     fetcho = FetchViaNxapi(target_url='http://10.201.30.194/ins', username='CISCO\\ambarik', password='xxxxxx')
#     print 'sw_version', repr(fetcho.sw_version)
#     print 'is_online', repr(fetcho.is_online)
#     print 'error_online', repr(fetcho.error_online)
#     print 'is_healthy', repr(fetcho.is_healthy)
#     print 'health_statuses', repr(fetcho.health_statuses)
#     print 'get_osinfo', fetcho.get_osinfo()
#     print 'get_intstats', fetcho.get_intstats()
#     print 'get_cpustats', fetcho.get_cpustats()
#     print 'get_memstats', fetcho.get_memstats()
#     print 'get_dirstats', fetcho.get_dirstats()
#     print 'get_dirstats', fetcho.get_dirstats()
#     print 'get_modulestats', fetcho.get_modulestats()
#     print 'test'
    
    
if __name__ == '__main__':
    main()
    