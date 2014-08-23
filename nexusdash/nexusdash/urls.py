from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

# My imports
from django.conf import settings
from .views import run_query

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'nexusdash.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    # Apps
    url('', include('hostnames.urls')),
    url('', include('dashboardperdevice.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^((?P<hostname>[\w.]+)/dash/)?query/', run_query),
    # url('^test/', include('test_app.urls')),
    # url('^cpu/', include('cpu_app.urls')),
)

# See: http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
