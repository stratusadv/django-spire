import json

from dandy.llm import MessageHistory
from dandy.llm.service.request.message import RoleLiteralStr
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from django_spire.ai.chat.messages import Message, MessageType
from django_spire.ai.chat.query_sets import ChatQuerySet
from django_spire.history.mixins import HistoryModelMixin


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

    def add_message(self, message: Message) -> None:
        ChatMessage.objects.create(
            chat=self,
            content=message.to_json(),
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

        messages = self.messages.order_by('-created_datetime')[:message_count]

        if exclude_last_message:
            messages = messages[1:]

        messages = list(reversed(messages))

        for message in messages:
            message_history.add_message(
                role=message.role,
                content=message.body
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

    content = models.JSONField()
    is_processed = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        body = json.loads(self.content)['body']

        if len(body) < 64:
            return body

        return body[:64] + '...'

    @property
    def body(self):
        return json.loads(self.content)['body']

    @property
    def role(self) -> RoleLiteralStr:
        message_type = json.loads(self.content)['type']
        if message_type == 'request':
            return 'user'
        elif message_type == 'response':
            return 'assistant'
        else:
            return 'system'

    def to_message(self, request) -> Message:
        content = json.loads(self.content)

        return Message(
            request=request,
            type=MessageType(content['type']),
            sender=content['sender'],
            body=content['body']
        )

    class Meta:
        db_table = 'django_spire_ai_chat_message'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'