from django.conf.urls import patterns, url
from .views import hostnames_page

urlpatterns = patterns('',
    url(r'^$', hostnames_page, name='home_page'),
)


