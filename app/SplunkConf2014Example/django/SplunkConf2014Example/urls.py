from django.conf.urls import patterns, include, url
from splunkdj.utility.views import render_template as render

urlpatterns = patterns('',
    url(r'^home/$', 'SplunkConf2014Example.views.home', name='home'),
    url(r'^setup/$', 'SplunkConf2014Example.views.setup', name='setup'),
)