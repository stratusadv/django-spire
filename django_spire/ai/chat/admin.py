from django.contrib import admin
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_spire.ai.chat import models


class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'view_chat_messages_link', 'created_datetime')
    search_fields = ('id', 'name')
    ordering = ['-id']

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


admin.site.register(models.Chat, ChatAdmin)
admin.site.register(models.ChatMessage)

