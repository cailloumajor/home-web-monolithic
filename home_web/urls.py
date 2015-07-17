#-*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.views.generic import TemplateView

from django.contrib import admin

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='base.html'), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^heating/', include('home_web.apps.heating.urls')),
]
