from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.authentication.mfa import models


@admin.register(models.MfaCode)
class MfaCodeAdmin(admin.ModelAdmin):
    list_display = ('id')
    list_filter = ('')
    search_fields = ('id')
    ordering = ('')

