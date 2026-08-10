from __future__ import annotations

from django.db import models


class AuthSmsCodePurposeChoices(models.TextChoices):
    ENROLLMENT = 'enro', 'Enrollment'
    SESSION = 'sess', 'Session'

