from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.comment import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id')
    list_filter = ('')
    search_fields = ('id')
    ordering = ('')

