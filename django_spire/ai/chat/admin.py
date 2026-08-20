from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from django_spire.ai.chat import models
from django_spire.contrib.admin.links import admin_changelist_url

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django.http import HttpRequest


@admin.register(models.Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'view_chat_messages_link', 'created_datetime')
    list_select_related = ('user',)
    ordering = ('-id',)
    search_fields = ('id', 'name')

    def get_queryset(self, request: HttpRequest) -> QuerySet[models.Chat]:
        queryset = super().get_queryset(request)

        return queryset.annotate(_message_count=Count('message', distinct=True))

    def get_readonly_fields(self, request: HttpRequest, obj: Model | None = None) -> list[str]:
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @admin.display(description='Messages', ordering='_message_count')
    def view_chat_messages_link(self, chat: models.Chat) -> str:
        url = admin_changelist_url(models.ChatMessage, chat__id=str(chat.id))

        return format_html('<a href="{}">{} Messages</a>', url, chat._message_count)


@admin.register(models.ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'content_body',
        'chat',
        'chat__user',
        'is_processed',
        'is_viewed',
        'created_datetime',
    )
    list_select_related = ('chat', 'chat__user')
    ordering = ('-id',)
    search_fields = ('id', 'sender', 'chat__name')

    @admin.display(description='Body')
    def content_body(self, chat_message: models.ChatMessage) -> str:
        return str(chat_message)

    def get_readonly_fields(self, request: HttpRequest, obj: Model | None = None) -> list[str]:
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
