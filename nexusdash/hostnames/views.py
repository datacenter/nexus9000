from django.views.generic import FormView
from django.http import HttpResponse
from .forms import LoginForm
from .models import HostNames
from .tasks import poll_healthinfo
import json

class HostNamesView(FormView):
    '''Home Page View with a popup Login Form
    '''
    template_name = "hostnames/index.html"
    form_class = LoginForm
    
    def get_context_data(self, **kwargs):
        '''
        Overriding get_context_data to add data for filling up Nexus Dashboard Table Template (in index.html)
        '''
        context = super(HostNamesView, self).get_context_data(**kwargs)
        devicesdata = list()
        
        for row in HostNames.objects.all():
            dd = dict()
            dd['url'] = row.url
            dd['hostname'] = row.hostname
            dd['is_online'] = row.is_online
            dd['is_healthy'] = row.is_healthy
            dd['username'] = row.username
            devicesdata.append(dd)
            
        context['devicesdata'] = devicesdata
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Overrides FormView.post in order to return JSON data for JS Validation (/js/login.js)
        # http://blackglasses.me/2013/10/08/custom-django-user-model-part-2/
        """
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        context = {}

        if form.is_valid():
            #cd = form.cleaned_data
            #print 'cleaned_data: {0}...'.format(repr(cd))
            context['success'] = 'Login Successful'
            user = form.save()      # user is the models.HostNames object
        else:
            context['errors'] = dict([(k, [unicode(e) for e in v]) for k,v in form.errors.items()])
            user = None
            #msg = "contact_page: Form in frontend and backend needs to be synced. Backend sees: {0}".format(form.errors)
            #print msg
            
        if user:
            hostname = user.hostname
            context['hostname'] = hostname
            poll_healthinfo.delay(hostname)
        return HttpResponse(json.dumps(context), content_type="application/json")
    
hostnames_page = HostNamesView.as_view()
