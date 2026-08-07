from __future__ import annotations

from django.db import models

from django_spire.auth.sms.choices import SmsAuthCodePurposeChoices
from django_spire.auth.sms.querysets import SmsAuthQuerySet
from django_spire.auth.sms.services.sms_auth_service import SmsAuthService
from django_spire.history.mixins import HistoryModelMixin


class SmsAuth(HistoryModelMixin):
    user = models.ForeignKey(
        'django_spire_auth_user.AuthUser',
        on_delete=models.CASCADE,
        related_name='sms_auths',
        related_query_name='sms_auth',
    )

    phone_number = models.CharField(max_length=20, unique=True)

    is_verified = models.BooleanField(default=False)
    verified_datetime = models.DateTimeField(blank=True, null=True)

    code_hash = models.CharField(max_length=128, blank=True, default='', editable=False)
    code_purpose = models.CharField(
        max_length=4,
        choices=SmsAuthCodePurposeChoices.choices,
        default='',
        blank=True,
        editable=False,
    )
    code_expiration_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    code_attempt_count = models.IntegerField(default=0, editable=False)

    session_started_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    session_last_activity_datetime = models.DateTimeField(blank=True, null=True, editable=False)

    objects = SmsAuthQuerySet.as_manager()

    services = SmsAuthService()

    def __str__(self) -> str:
        return f'{self.phone_number} ({self.user})'

    class Meta:
        db_table = 'django_spire_auth_sms'
        verbose_name = 'SMS Auth'
        verbose_name_plural = 'SMS Auths'
        ordering = ('phone_number',)
