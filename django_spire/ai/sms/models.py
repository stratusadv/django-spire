from __future__ import annotations

from dandy.llm.request.message import MessageHistory, RoleLiteralStr
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from django_spire.ai.sms.querysets import SmsConversationQuerySet, SmsMessageQuerySet
from django_spire.history.mixins import HistoryModelMixin


class SmsConversation(HistoryModelMixin):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sms_conversations',
        related_query_name='sms_conversation'
    )

    phone_number = models.CharField(max_length=20)
    last_message_datetime = models.DateTimeField(default=now, editable=False)

    objects = SmsConversationQuerySet.as_manager()

    def __str__(self):
        return f"SMS Conversation with {self.phone_number}"

    def add_message(
        self,
        body: str,
        is_inbound: bool,
        twilio_sid: str,
        is_processed: bool = False
    ):
        message = self.messages.create(
            body=body,
            is_inbound=is_inbound,
            twilio_sid=twilio_sid,
            is_processed=is_processed,
        )

        self.last_message_datetime = now()
        self.save()

        return message

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
            message_history.create_message(
                role=message.role,
                text=message.body
            )

        return message_history

    @property
    def is_empty(self) -> bool:
        return self.messages.count() == 0

    class Meta:
        db_table = 'django_spire_ai_sms_conversation'
        verbose_name = 'SMS Conversation'
        verbose_name_plural = 'SMS Conversations'
        ordering = ('-last_message_datetime',)


class SmsMessage(HistoryModelMixin):
    conversation = models.ForeignKey(
        SmsConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        related_query_name='message'
    )

    body = models.TextField()

    is_inbound = models.BooleanField(default=False)

    twilio_sid = models.CharField(max_length=64, blank=True, null=True)

    is_processed = models.BooleanField(default=False)

    objects = SmsMessageQuerySet.as_manager()

    def __str__(self):
        if len(self.body) < 64:
            return f"{self.direction}: {self.body}"

        return f"{self.direction}: {self.body[:64]}..."

    @property
    def direction(self) -> str:
        return "Inbound" if self.is_inbound else "Outbound"

    @property
    def is_outbound(self) -> bool:
        return not self.is_inbound

    @property
    def role(self) -> RoleLiteralStr:
        if self.is_inbound:
            return 'user'

        if self.is_outbound:
            return 'assistant'

        return 'system'

    class Meta:
        db_table = 'django_spire_ai_sms_message'
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'
        ordering = ('-created_datetime',)
