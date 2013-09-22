from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.pools, name='pools_list'),
    url(r'add/$', views.add, name='pool_add'),
    url(r'remove/(?P<POOL>\d+)/$', views.remove, name='pool_remove'),
    url(r'switch/(?P<POOL>\d+)/$', views.switch, name='pool_switch'),
    url(r'enable/(?P<POOL>\d+)/$', views.enable, name='pool_enable'),
    url(r'disable/(?P<POOL>\d+)/$', views.disable, name='pool_disable'),
)
