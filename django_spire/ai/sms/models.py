from __future__ import annotations

import secrets

from datetime import timedelta

from dandy.llm.request.message import MessageHistory, RoleLiteralStr
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from django_spire.ai.sms.querysets import (
    SmsConversationQuerySet,
    SmsMessageQuerySet,
    SmsPhoneNumberQuerySet,
)
from django_spire.conf import settings
from django_spire.history.mixins import HistoryModelMixin


CODE_DIGIT_COUNT = 6


class SmsCodePurposeChoices(models.TextChoices):
    ENROLLMENT = 'enrollment', 'Enrollment'
    SESSION = 'session', 'Session'


class SmsPhoneNumber(HistoryModelMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sms_phone_numbers',
        related_query_name='sms_phone_number',
    )

    phone_number = models.CharField(max_length=20, unique=True)

    is_verified = models.BooleanField(default=False)
    verified_datetime = models.DateTimeField(blank=True, null=True)

    code_hash = models.CharField(max_length=128, blank=True, default='', editable=False)
    code_purpose = models.CharField(
        max_length=16,
        blank=True,
        choices=SmsCodePurposeChoices.choices,
        default='',
        editable=False,
    )
    code_expiration_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    code_attempt_count = models.IntegerField(default=0, editable=False)

    session_started_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    session_last_activity_datetime = models.DateTimeField(blank=True, null=True, editable=False)

    objects = SmsPhoneNumberQuerySet.as_manager()

    def __str__(self) -> str:
        return f'{self.phone_number} ({self.user})'

    def code_clear(self) -> None:
        self.code_hash = ''
        self.code_purpose = ''
        self.code_expiration_datetime = None
        self.code_attempt_count = 0
        self.save()

    def code_confirm(self, code: str, purpose: str) -> bool:
        if self.code_hash == '':
            return False

        if self.code_purpose != purpose:
            return False

        if self.code_expiration_datetime is None:
            return False

        if now() > self.code_expiration_datetime:
            self.code_clear()
            return False

        attempt_count_max = settings.DJANGO_SPIRE_AI_SMS_CODE_ATTEMPT_COUNT_MAX

        if self.code_attempt_count >= attempt_count_max:
            self.code_clear()
            return False

        if not check_password(code, self.code_hash):
            self.code_attempt_count += 1
            self.save()
            return False

        self.code_clear()

        return True

    def code_issue(self, purpose: str) -> str:
        if purpose not in SmsCodePurposeChoices.values:
            message = f'unknown sms code purpose: {purpose}'
            raise ValueError(message)

        code = f'{secrets.randbelow(10 ** CODE_DIGIT_COUNT):0{CODE_DIGIT_COUNT}d}'
        expiry_minutes = settings.DJANGO_SPIRE_AI_SMS_CODE_EXPIRY_MINUTES

        self.code_hash = make_password(code)
        self.code_purpose = purpose
        self.code_expiration_datetime = now() + timedelta(minutes=expiry_minutes)
        self.code_attempt_count = 0
        self.save()

        return code

    def session_close(self) -> None:
        self.session_started_datetime = None
        self.session_last_activity_datetime = None
        self.save()

    @property
    def session_is_active(self) -> bool:
        if self.session_started_datetime is None:
            return False

        if self.session_last_activity_datetime is None:
            return False

        duration_minutes_max = settings.DJANGO_SPIRE_AI_SMS_SESSION_DURATION_MINUTES_MAX
        idle_minutes_max = settings.DJANGO_SPIRE_AI_SMS_SESSION_IDLE_MINUTES_MAX

        duration_deadline = self.session_started_datetime + timedelta(minutes=duration_minutes_max)
        idle_deadline = self.session_last_activity_datetime + timedelta(minutes=idle_minutes_max)

        current_datetime = now()

        if current_datetime > duration_deadline:
            return False

        if current_datetime > idle_deadline:
            return False

        return True

    def session_open(self) -> None:
        current_datetime = now()

        self.session_started_datetime = current_datetime
        self.session_last_activity_datetime = current_datetime
        self.save()

    def session_touch(self) -> None:
        self.session_last_activity_datetime = now()
        self.save()

    def verified_mark(self) -> None:
        self.is_verified = True
        self.verified_datetime = now()
        self.save()

    class Meta:
        db_table = 'django_spire_ai_sms_phone_number'
        verbose_name = 'SMS Phone Number'
        verbose_name_plural = 'SMS Phone Numbers'
        ordering = ('phone_number',)


class SmsConversation(HistoryModelMixin):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='sms_conversations',
        related_query_name='sms_conversation',
    )

    phone_number = models.CharField(max_length=20)
    last_message_datetime = models.DateTimeField(default=now, editable=False)

    objects = SmsConversationQuerySet.as_manager()

    def __str__(self) -> str:
        return f'SMS Conversation with {self.phone_number}'

    def add_message(
        self, body: str, is_inbound: bool, twilio_sid: str, is_processed: bool = False
    ) -> SmsMessage:
        message = self.messages.create(
            body=body, is_inbound=is_inbound, twilio_sid=twilio_sid, is_processed=is_processed
        )

        self.last_message_datetime = now()
        self.save()

        return message

    def generate_message_history(
        self, message_count: int = 20, exclude_last_message: bool = True
    ) -> MessageHistory:
        message_history = MessageHistory()

        messages = self.messages.newest_by_count(message_count)

        if exclude_last_message:
            messages = messages[1:]

        messages = list(reversed(messages))

        for message in messages:
            message_history.add_message(role=message.role, text=message.body)

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
        related_query_name='message',
    )

    body = models.TextField()

    is_inbound = models.BooleanField(default=False)

    twilio_sid = models.CharField(max_length=64, blank=True, null=True)

    is_processed = models.BooleanField(default=False)

    objects = SmsMessageQuerySet.as_manager()

    def __str__(self) -> str:
        if len(self.body) < 64:
            return f'{self.direction}: {self.body}'

        return f'{self.direction}: {self.body[:64]}...'

    @property
    def direction(self) -> str:
        return 'Inbound' if self.is_inbound else 'Outbound'

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
