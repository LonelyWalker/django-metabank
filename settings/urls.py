from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^$', views.Network.as_view(), name='settings_network'),
    url(r'^edit_interface/$', views.EditInterface.as_view(), name='settings_edit_interface'),
)
