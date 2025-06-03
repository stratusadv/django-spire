from django.contrib import admin

from django_spire.ai.sms.models import SmsConversation, SmsMessage


class SmsMessageInline(admin.TabularInline):
    model = SmsMessage
    extra = 0
    readonly_fields = ('created_datetime', )
    fields = ('body', 'is_inbound', 'is_processed', 'twilio_sid', 'created_datetime')


@admin.register(SmsConversation)
class SmsConversationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'user', 'last_message_datetime', 'has_unread_messages')
    list_filter = ('has_unread_messages',)
    search_fields = ('phone_number', 'user__username', 'user__email')
    readonly_fields = ('created_datetime', )
    inlines = [SmsMessageInline]


@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'conversation', 'is_inbound', 'is_processed', 'created_datetime')
    list_filter = ('is_inbound', 'is_processed')
    search_fields = ('body', 'conversation__phone_number')
    readonly_fields = ('created_datetime', )