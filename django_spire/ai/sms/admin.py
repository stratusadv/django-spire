from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_spire.ai.sms.models import SmsConversation, SmsMessage


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    extra = 0
    readonly_fields = ('created_datetime', )
    fields = ('body', 'is_inbound', 'is_processed', 'twilio_sid', 'created_datetime')


@admin.register(SmsConversation)
class SmsConversationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'last_message_datetime', 'view_sms_messages_link')
    search_fields = ('phone_number', 'user__username', 'user__email')
    readonly_fields = ('created_datetime', )
    inlines = [SmsMessageInline]

    def view_sms_messages_link(self, obj):
        count = obj.messages.count()
        url = (
                reverse("admin:django_spire_ai_sms_smsmessage_changelist")
                + "?"
                + urlencode({"sms_conversation__id": f"{obj.id}"})
        )
        return format_html('<a href="%s">%s Messages</a>' % (url, count))

    view_sms_messages_link.short_description = "Messages"

    class Meta:
        ordering = ('phone_number', )



@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'conversation', 'is_inbound', 'is_processed', 'created_datetime')
    list_filter = ('is_inbound', 'is_processed')
    search_fields = ('body', 'conversation__phone_number')
    readonly_fields = ('created_datetime', )

    class Meta:
        ordering = ('created_datetime', )