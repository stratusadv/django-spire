from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.user_account.profile import models


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id')
    list_filter = ('')
    search_fields = ('id')
    ordering = ('')

