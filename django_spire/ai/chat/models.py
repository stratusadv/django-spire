from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from django_spire.ai.chat.query_sets import ChatQuerySet
from django_spire.history.mixins import HistoryModelMixin

if TYPE_CHECKING:
    from django_spire.ai.chat.messages import Message


class Chat(HistoryModelMixin):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='chats',
        related_query_name='chat'
    )

    name = models.CharField(max_length=128)
    last_message_datetime = models.DateTimeField(default=now, editable=False)
    has_unread_messages = models.BooleanField(default=False)

    objects = ChatQuerySet.as_manager()

    def add_message(self, message: Message) -> None:
        ChatMessage.objects.create(
            chat=self,
            content=message.to_json(),
        )

    class Meta:
        db_table = 'spire_ai_chat'
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'


class ChatMessage(HistoryModelMixin):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='message'
    )

    content = models.JSONField()
    is_processed = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)

    class Meta:
        db_table = 'spire_ai_chat_message'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'