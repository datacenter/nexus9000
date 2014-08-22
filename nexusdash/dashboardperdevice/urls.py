from django.conf.urls import patterns, url
from .views import dashboard_view

urlpatterns = patterns('',
    url(r'^(?P<hostname>[\w.]+)/dash/$', dashboard_view), # http://stackoverflow.com/a/157295/558397
)

