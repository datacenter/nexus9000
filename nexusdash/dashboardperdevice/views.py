from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from hostnames.models import HostNames
from django.http import Http404

class DashboardPerDeviceView(TemplateView):
    template_name = "dashboardperdevice/dashboardperdevice.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        hostname = kwargs.get('hostname')
        if len(HostNames.objects.filter(hostname=hostname)) == 0:
            raise Http404
        return self.render_to_response(context)
    
dashboard_view = DashboardPerDeviceView.as_view()
