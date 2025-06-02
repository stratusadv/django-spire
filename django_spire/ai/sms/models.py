from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

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
    has_unread_messages = models.BooleanField(default=False)

    def __str__(self):
        return f"SMS Conversation with {self.phone_number}"

    def add_message(self, body, is_inbound=False):
        message = self.messages.create(
            body=body,
            is_inbound=is_inbound,
            is_processed=False,
        )

        self.last_message_datetime = now()
        self.has_unread_messages = is_inbound
        self.save()

        return message

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
    is_processed = models.BooleanField(default=False)

    twilio_sid = models.CharField(max_length=64, blank=True, null=True)

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

    class Meta:
        db_table = 'django_spire_ai_sms_message'
        verbose_name = 'SMS Message'
        verbose_name_plural = 'SMS Messages'
        ordering = ('-created_datetime',)