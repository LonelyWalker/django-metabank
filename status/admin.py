# -*- coding:utf-8 -*-
from django.contrib import admin
from models import LogAverage

class LogAverageAdmin(admin.ModelAdmin):
    pass

admin.site.register(LogAverage, LogAverageAdmin)
