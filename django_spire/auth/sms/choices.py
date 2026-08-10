from __future__ import annotations

from django.db import models


class AuthSmsCodePurposeChoices(models.TextChoices):
    VERIFICATION = 'veri', 'Verification'
    SESSION = 'sess', 'Session'

