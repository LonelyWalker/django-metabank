from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'status.views.index', name='index'),
    url(r'^status/realtime/$', 'status.views.realtime', name='realtime'),
    url(r'^status/realtime_data/$', 'status.views.realtime_data', name='realtime_data'),
    url(r'^status/av_data/$', 'status.views.av_data', name='av_data'),
    url(r'^status/chip-info/$', 'status.views.chipinfo', name='chip-info'),

    url(r'^pools/', include('pools.urls')),
    url(r'^settings/', include('settings.urls')),
    url(r'^log/', include('logview.urls')),

    url(r'^login/$',  'django.contrib.auth.views.login',  {'template_name': 'auth/login.html'}, name='auth_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),

    url(r'^admin/', include(admin.site.urls)),
)
