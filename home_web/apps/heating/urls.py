#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

from . import views

api_patterns = patterns('',
    url(r'^modes/$', views.ModeAPI.as_view(), name='api_mode'),
)

urlpatterns = patterns('',
    url(r'^$', views.ZoneList.as_view(), name='zone_list'),
    url(r'^slot/new/zone_(?P<zone>\d)/$', views.SlotCreate.as_view(),
        name='new_slot'),
    url(r'^slot/(?P<pk>\d+)/$', views.SlotUpdate.as_view(), name='update_slot'),
    url(r'^slot/(?P<pk>\d+)/delete/$', views.SlotDelete.as_view(), name='del_slot'),
    url(r'^api/', include(api_patterns)),
)
