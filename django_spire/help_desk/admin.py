from __future__ import annotations

from django.contrib import admin

from django_spire.help_desk.models import HelpDeskTicket


@admin.register(HelpDeskTicket)
class HelpDeskTicketAdmin(admin.ModelAdmin):
    list_display = ('pk', 'purpose', 'priority', 'status', 'created_by', 'created_datetime')
    list_filter = ('priority', 'purpose', 'status', 'is_active', 'is_deleted')
    ordering = ('-created_datetime',)
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_by', 'created_datetime', 'is_active', 'is_deleted')
    search_fields = ('description', 'created_by__username', 'created_by__email')
