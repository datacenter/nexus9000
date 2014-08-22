# Create your views here.
from django.views.generic import TemplateView
from django.http import HttpResponse
from hostnames.views import HostNamesView
from django.template import loader, Context
from hostnames.models import HostNames
from dashboardperdevice.tasks import poll_intstats
from dashboardperdevice.tasks import poll_cpustats
from dashboardperdevice.tasks import poll_memstats
from dashboardperdevice.tasks import poll_dirstats
from dashboardperdevice.tasks import poll_modulestats
from dashboardperdevice.models import InterfacesStats
from dashboardperdevice.models import CpuStats
from dashboardperdevice.models import MemStats
from dashboardperdevice.models import DirStats
from dashboardperdevice.models import ModulesStats
from hostnames.tasks import poll_healthinfo
from django.conf import settings
from nvd3 import lineWithFocusChart
import json


class My404View(TemplateView):
    # TODO: Find a better way and update 404.html html
    template_name = "404.html"
    
my404_page = My404View.as_view()

class RunQueryView(TemplateView):
    '''Returns JSON data based on querying the sql db, after getting the latest data
    This JSON gets used by dashboard.*.js files
    
    Particularly, this method gets called when user goes to
    http://myurl/query?module=modulename, where the modulename needs to match
    parameter of "this.fillElement()" in dashboard.perdevice.js
    and "moduleData()" in dashboard.index.js
    '''

    def get(self, request, *args, **kwargs):
        '''
        Overriding get to return only JSON.
        '''
        context = {} # self.get_context_data(**kwargs)
        hostname = kwargs.get('hostname')
        data_requested = self.request.GET.get('module')
        context['module'] = data_requested
        if data_requested == 'hostnames':
            # Update HostNames DB
            for row in HostNames.objects.all():
                poll_healthinfo.delay(row.hostname)
                
            # Retrieve data from DB and return the table body
            # http://www.djangobook.com/en/2.0/chapter04.html
            cdata = HostNamesView().get_context_data()
            t = loader.get_template('hostnames/hostnames.table.html')
            tbody_html = t.render(Context(cdata))
            context['data'] = tbody_html
            
        elif hostname:
            if data_requested == 'osinfo':
                from dashboardperdevice.tasks import poll_osinfo
                from dashboardperdevice.models import OSInfo
                poll_osinfo.delay(hostname=hostname)
                cdata = dict()
                try:
                    o = OSInfo.objects.get(hostname__hostname=hostname)
                    cdata['ostime'] = o.ostime
                    cdata['osuptime'] = o.osuptime
                    cdata['osplatform'] = o.osplatform
                    cdata['osdevicename'] = o.osdevicename
                except:
                    pass
                
                t = loader.get_template('dashboardperdevice/osinfo.table.html')
                tbody_html = t.render(Context(cdata))
                context['data'] = tbody_html
                
            elif data_requested == 'overallhealth':
                poll_healthinfo.delay(hostname)
                hostname_obj = HostNames.objects.get(hostname=hostname)
                cdata = dict()
                cdata['error_online'] = hostname_obj.error_online
                try:
                    hs = eval(hostname_obj.health_statuses)
                except:
                    hs = list()
                else:
                    if not isinstance(hs, list):
                        hs = list()
                cdata['health_statuses'] = hs
                t = loader.get_template('dashboardperdevice/overallhealth.table.html')
                tbody_html = t.render(Context(cdata))
                context['data'] = tbody_html
                
            elif data_requested == 'intstats':
                poll_intstats.delay(hostname=hostname)
                intstats_table_data = list()
                hs = InterfacesStats.objects.filter(hostname__hostname=hostname)
                last_timestamp = hs.latest('polling_timestamp').polling_timestamp
                last_poll = hs.filter(polling_timestamp=last_timestamp)
                
                # Create table data
                for r in last_poll:
                    status = '{0}/{1}'.format(r.int_state, r.int_adminstate)
                    if r.int_ipaddr == r.int_ipmask == '':
                        ip = ''
                    else:
                        ip = '{0}/{1}'.format(r.int_ipaddr, r.int_ipmask)
                    provided_interval = int(HostNames.objects.get(hostname=hostname).polling_interval)
                    interval = int(r.int_loadinterval) + provided_interval
                    e = [r.int_name, status, r.int_hwdesc, ip, r.int_hwaddr,
                         r.int_mtu, r.int_bw, r.int_desc, r.int_bpsrate_rx,
                         r.int_bpsrate_tx, interval]
                    intstats_table_data.append(e)
                context['data'] = intstats_table_data
                
                # Graph related
                # https://github.com/mbostock/d3/wiki/Time-Formatting
                charts_content = list()     # Nested list: [(int_name, html_chart_content),] for JSON data
                tooltip_date = "%d %b %Y %H:%M:%S %p"
                try:
                    unique_interfaces = hs.values_list('int_name').distinct()
                    up_unique_interfaces = unique_interfaces.filter(int_state='up')
                    up_unique_interfaces_with_bps = up_unique_interfaces.exclude(int_bpsrate_tx='', int_bpsrate_rx='')
                    list_of_interfaces = zip(*up_unique_interfaces_with_bps)[0]
                except IndexError:
                    list_of_interfaces = list()
                for int_name in list_of_interfaces:
                    per_int_entries = hs.filter(int_name=int_name).order_by('polling_timestamp')
                    try:
                        xdata = zip(*per_int_entries.values_list('polling_timestamp'))[0]
                        def int_n_mult(i):
                            return int(i)*settings.D3_PY_TIME_DIFF
                        xdata = list(map(int_n_mult, xdata))
                        ydata_tx = zip(*per_int_entries.values_list('int_bpsrate_tx'))[0]
                        ydata_tx = list(map(int, ydata_tx))
                        ydata_rx = zip(*per_int_entries.values_list('int_bpsrate_rx'))[0]
                        ydata_rx = list(map(int, ydata_rx))
                    except IndexError:
                        xdata = list()
                        ydata_tx = list()
                        ydata_rx = list()
                        
                    try:
                        int_latest_state = per_int_entries.reverse()[0].int_state
                    except IndexError:
                        int_latest_state = 'NA'
                    name_display_rx = 'Input/Rx (bps) - {name} ({state})'.format(name=int_name, state=int_latest_state)
                    name_display_tx = 'Output/Tx (bps) - {name} ({state})'.format(name=int_name, state=int_latest_state)
                    extra_serie = {"tooltip": {"y_start": "Rate ", "y_end": "bps"},
                                   "date_format": tooltip_date}
                    chart = lineWithFocusChart(name='interfaceStatsGraph-{0}'.format(int_name), 
                                               x_is_date=True, x_axis_format="%H:%M:%S")
                    try:
                        chart.add_serie(y=ydata_tx, x=xdata, name=name_display_tx, extra=extra_serie)
                        chart.add_serie(y=ydata_rx, x=xdata, name=name_display_rx, extra=extra_serie)
                        chart.buildcontent()
                        charts_content.append([int_name, chart.htmlcontent])
                    except IndexError:
                        pass
                        
                context['graph_data'] = charts_content
                
            elif data_requested == 'loadavg':
                poll_cpustats.delay(hostname=hostname)
                hs = CpuStats.objects.filter(hostname__hostname=hostname)
                last_timestamp = hs.latest('polling_timestamp').polling_timestamp
                last_poll = hs.filter(polling_timestamp=last_timestamp)
                try:
                    vals = last_poll.values_list('per1min', 'per5min', 'per15min')[0]
                    percents = [int(float(i)*100) for i in vals]
                    cpudata = zip(vals, percents)
                except IndexError:
                    cpudata = list()
                context['data'] = cpudata
            
            elif data_requested == 'mem':
                poll_memstats.delay(hostname=hostname)
                hs = MemStats.objects.filter(hostname__hostname=hostname)
                last_timestamp = hs.latest('polling_timestamp').polling_timestamp
                last_poll = hs.filter(polling_timestamp=last_timestamp)
                try:
                    memdata = last_poll.values_list('mem_total', 'mem_used', 'mem_free')[0]
                except IndexError:
                    memdata = list()
                context['data'] = memdata
                
            elif data_requested == 'df':
                poll_dirstats.delay(hostname=hostname)
                hs = DirStats.objects.filter(hostname__hostname=hostname)
                last_timestamp = hs.latest('polling_timestamp').polling_timestamp
                last_poll = hs.filter(polling_timestamp=last_timestamp)
                diskdata = last_poll.values_list('dirpath', 'total', 'used', 'free', 'used_percent', 'module')
                diskdata = [list(i) for i in diskdata]
                context['data'] = diskdata
                
            elif data_requested == 'modstats':
                poll_modulestats.delay(hostname=hostname)
                hs = ModulesStats.objects.filter(hostname__hostname=hostname)
                last_timestamp = hs.latest('polling_timestamp').polling_timestamp
                last_poll = hs.filter(polling_timestamp=last_timestamp)
                modinfo = last_poll.values_list('mod_id', 'ports', 'hw_desc', 'hw_model', 'serial_no', 'status', 'diag_stat')
                modinfo = [list(i) for i in modinfo]
                context['data'] = modinfo
                
        return HttpResponse(json.dumps(context), content_type="application/json")
    
run_query = RunQueryView.as_view()