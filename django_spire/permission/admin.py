from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.permission import models


@admin.register(models.PortalGroup)
class PortalGroupAdmin(admin.ModelAdmin):
    list_display = ('id')
    list_filter = ('')
    search_fields = ('id')
    ordering = ('')


@admin.register(models.PortalUser)
class PortalUserAdmin(admin.ModelAdmin):
    list_display = ('id')
    list_filter = ('')
    search_fields = ('id')
    ordering = ('')

