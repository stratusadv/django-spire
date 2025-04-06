from django.contrib import admin

from django_spire.ai import models


@admin.register(models.AiInteraction)
class AiInteractionAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'app_name', 'created_datetime')
    list_filter = ('app_name',)
    search_fields = ('user_email', 'user_first_name', 'user_last_name', 'app_name')
    ordering = ('-created_datetime',)
