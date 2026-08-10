from __future__ import annotations

from datetime import timedelta

from django.core.cache import cache
from django.db import models
from django.utils.timezone import now

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.querysets import AuthSmsQuerySet
from django_spire.auth.sms.services.service import AuthSmsService
from django_spire.conf import settings
from django_spire.history.mixins import HistoryModelMixin

DAY_SECONDS = 86400
MINUTE_SECONDS = 60


class AuthSms(HistoryModelMixin):
    user = models.ForeignKey(
        'django_spire_auth_user.AuthUser',
        on_delete=models.CASCADE,
        related_name='auth_smss',
        related_query_name='auth_sms',
    )

    phone_number = models.CharField(max_length=20, unique=True)

    is_verified = models.BooleanField(default=False)
    verified_datetime = models.DateTimeField(blank=True, null=True)

    code_hash = models.CharField(max_length=128, blank=True, default='', editable=False)
    code_purpose = models.CharField(
        max_length=4,
        choices=AuthSmsCodePurposeChoices.choices,
        default='',
        blank=True,
        editable=False,
    )
    code_expiration_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    code_attempt_count = models.IntegerField(default=0, editable=False)

    session_started_datetime = models.DateTimeField(blank=True, null=True, editable=False)
    session_last_activity_datetime = models.DateTimeField(blank=True, null=True, editable=False)

    objects = AuthSmsQuerySet.as_manager()

    services = AuthSmsService()

    def __str__(self) -> str:
        return f'{self.phone_number} ({self.user})'

    @property
    def session_is_active(self) -> bool:
        if self.session_started_datetime is None:
            return False

        if self.session_last_activity_datetime is None:
            return False

        duration_minutes_max = settings.DJANGO_SPIRE_AUTH_SMS_SESSION_DURATION_MINUTES_MAX
        idle_minutes_max = settings.DJANGO_SPIRE_AUTH_SMS_SESSION_IDLE_MINUTES_MAX

        duration_deadline = self.session_started_datetime + timedelta(
            minutes=duration_minutes_max
        )
        idle_deadline = self.session_last_activity_datetime + timedelta(
            minutes=idle_minutes_max
        )

        current_datetime = now()

        if current_datetime > duration_deadline:
            return False

        return not current_datetime > idle_deadline

    def throttle_allowed(self) -> bool:
        current_datetime = now()

        minute_window = current_datetime.strftime('%Y%m%d%H%M')
        day_window = current_datetime.strftime('%Y%m%d')

        minute_key = f'django_spire_auth_sms_throttle_minute_{self.phone_number}_{minute_window}'
        day_key = f'django_spire_auth_sms_throttle_day_{self.phone_number}_{day_window}'

        minute_count = self._counter_increment(minute_key, MINUTE_SECONDS)
        day_count = self._counter_increment(day_key, DAY_SECONDS)

        minute_rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE
        day_rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_DAY

        if minute_count > minute_rate_max:
            return False

        return not day_count > day_rate_max

    @staticmethod
    def _counter_increment(key: str, timeout_seconds: int) -> int:
        cache.add(key, 0, timeout_seconds)

        return cache.incr(key)

    class Meta:
        db_table = 'django_spire_auth_sms'
        verbose_name = 'Auth SMS'
        verbose_name_plural = 'Auth SMSs'
        ordering = ('phone_number',)
