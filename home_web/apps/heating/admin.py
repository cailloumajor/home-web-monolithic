#-*- coding: utf-8 -*-

from django.contrib import admin
from .models import Zone

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('num', 'desc')
    
admin.site.register(Zone, ZoneAdmin)
