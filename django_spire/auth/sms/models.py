from __future__ import annotations

from datetime import datetime, timedelta

from django.core.cache import cache
from django.db import models
from django.utils.timezone import now, localtime

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

    def _build_throttle_keys(self) -> tuple[str, str]:
        current_datetime = localtime()
        minute_window = current_datetime.strftime('%Y%m%d%H%M')
        day_window = current_datetime.strftime('%Y%m%d')

        minute_key = f'django_spire_auth_sms_throttle_minute_{self.phone_number}_{minute_window}'
        day_key = f'django_spire_auth_sms_throttle_day_{self.phone_number}_{day_window}'

        return minute_key, day_key

    def is_throttled(self) -> bool:
        minute_key, day_key = self._build_throttle_keys()

        minute_count = cache.get(minute_key, 0) or 0
        day_count = cache.get(day_key, 0) or 0

        minute_rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE
        day_rate_max = settings.DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_DAY

        if minute_count > minute_rate_max:
            return True

        return day_count > day_rate_max

    def record_attempt(self) -> None:
        minute_key, day_key = self._build_throttle_keys()

        cache.add(minute_key, 0, MINUTE_SECONDS)
        cache.incr(minute_key)

        cache.add(day_key, 0, DAY_SECONDS)
        cache.incr(day_key)

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

    class Meta:
        db_table = 'django_spire_auth_sms'
        verbose_name = 'Auth SMS'
        verbose_name_plural = 'Auth SMSs'
        ordering = ('phone_number',)
