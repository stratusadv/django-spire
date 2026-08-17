from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from django_spire.ai.sms.models import SmsConversation, SmsMessage
from django_spire.contrib.admin.links import admin_changelist_url

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    extra = 0
    fields = ('body', 'is_inbound', 'is_processed', 'twilio_sid', 'created_datetime')
    readonly_fields = ('created_datetime',)


@admin.register(SmsConversation)
class SmsConversationAdmin(admin.ModelAdmin):
    inlines = (SmsMessageInline,)

    list_display = ('phone_number', 'user', 'last_message_datetime', 'view_sms_messages_link')
    list_select_related = ('user',)
    ordering = ('-last_message_datetime',)
    readonly_fields = ('created_datetime',)
    search_fields = ('phone_number', 'user__username', 'user__email')

    def get_queryset(self, request: HttpRequest) -> QuerySet[SmsConversation]:
        queryset = super().get_queryset(request)

        return queryset.annotate(_message_count=Count('message', distinct=True))

    @admin.display(description='Messages', ordering='_message_count')
    def view_sms_messages_link(self, conversation: SmsConversation) -> str:
        url = admin_changelist_url(SmsMessage, conversation__id=str(conversation.id))

        return format_html('<a href="{}">{} Messages</a>', url, conversation._message_count)


@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'conversation', 'is_inbound', 'is_processed', 'created_datetime')
    list_filter = ('is_inbound', 'is_processed')
    list_select_related = ('conversation',)
    ordering = ('-created_datetime',)
    readonly_fields = ('created_datetime',)
    search_fields = ('body', 'conversation__phone_number')
