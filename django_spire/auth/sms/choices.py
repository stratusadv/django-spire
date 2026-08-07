from __future__ import annotations

from django.db import models


class SmsAuthCodePurposeChoices(models.TextChoices):
    ENROLLMENT = 'enro', 'Enrollment'
    SESSION = 'sess', 'Session'

