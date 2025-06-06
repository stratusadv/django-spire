import json

from dandy.llm import MessageHistory
from dandy.llm.service.request.message import RoleLiteralStr
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from django_spire.ai.chat.messages import BaseMessageIntel
from django_spire.ai.chat.responses import MessageResponse
from django_spire.ai.chat.choices import MessageResponseType
from django_spire.ai.chat.querysets import ChatQuerySet, ChatMessageQuerySet
from django_spire.history.mixins import HistoryModelMixin
from django_spire.utils import get_class_from_string, get_class_name_from_class


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

    def __str__(self):
        if len(self.name) < 48:
            return self.name

        return self.name[:48] + '...'

    def add_message_response(self, message_response: MessageResponse) -> None:
        self.messages.create(
            response_type=message_response.type.value,
            sender=message_response.sender,
            _intel_data=message_response.message_intel.model_dump(),
            _intel_class_name=get_class_name_from_class(message_response.message_intel.__class__),
            is_processed=True,
            is_viewed=True
        )
        self.last_message_datetime = now()
        self.save()

    def generate_message_history(
            self,
            message_count: int = 20,
            exclude_last_message: bool = True
    ) -> MessageHistory:
        message_history = MessageHistory()

        messages = self.messages.newest_by_count(message_count)

        if exclude_last_message:
            messages = messages[1:]

        messages = list(reversed(messages))

        for message in messages:
            message_history.add_message(
                role=message.role,
                content=message.intel.content_to_str()
            )

        return message_history

    @property
    def is_empty(self) -> bool:
        return self.messages.count() == 0

    @property
    def name_shortened(self) -> str:
        if len(self.name) > 24:
            return self.name[:24] + '...'

        return self.name

    class Meta:
        db_table = 'django_spire_ai_chat'
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        ordering = ('-last_message_datetime', 'name')


class ChatMessage(HistoryModelMixin):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='message'
    )

    response_type = models.CharField(max_length=32, choices=MessageResponseType)
    sender = models.CharField(max_length=128)
    _intel_data = models.JSONField()
    _intel_class_name = models.TextField()
    is_processed = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)

    objects = ChatMessageQuerySet.as_manager()

    def __str__(self):
        content = self.intel.content_to_str()

        if len(content) < 64:
            return content

        return content[:64] + '...'

    @property
    def intel(self):
        intel_class: BaseMessageIntel = get_class_from_string(self._intel_class_name)
        return intel_class.model_validate(self._intel_data)

    @intel.setter
    def intel(self, message_intel: BaseMessageIntel):
        self._intel_class_name = get_class_name_from_class(message_intel.__class__)
        self._intel_data = message_intel.model_dump()

    @property
    def role(self) -> RoleLiteralStr:
        if self.response_type == 'request':
            return 'user'
        elif self.response_type == 'response':
            return 'assistant'
        else:
            return 'system'

    def to_message_response(self) -> MessageResponse:
        return MessageResponse(
            type=MessageResponseType(self.response_type),
            sender=self.sender,
            message_intel=self.intel
        )

    class Meta:
        db_table = 'django_spire_ai_chat_message'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
