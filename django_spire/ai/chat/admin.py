from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.ai.chat import models

@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'view_chat_messages_link', 'created_datetime')
    search_fields = ('id', 'name')
    ordering = ['-id']

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def view_chat_messages_link(self, obj):
        count = obj.messages.count()
        url = (
                reverse("admin:spire_ai_chat_chatmessage_changelist")
                + "?"
                + urlencode({"chat__id": f"{obj.id}"})
        )
        return format_html('<a href="%s">%s Messages</a>' % (url, count))

    view_chat_messages_link.short_description = "Messages"

    class Meta:
        ordering = ('id', )


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('content_body', 'chat', 'chat__user','is_processed', 'is_viewed', 'created_datetime')
    search_fields = ('id', 'content')
    ordering = ['-id']

    def content_body(self, obj):
        return str(obj)

    content_body.short_description = 'Body'

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

