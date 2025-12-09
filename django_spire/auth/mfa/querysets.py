from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet
from django.utils.timezone import localtime

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_spire.auth.mfa.models import MfaCode


class MfaCodeQuerySet(QuerySet):
    def valid_code(self, user: User) -> MfaCode | None:
        return self.filter(user=user, expiration_datetime__gt=localtime()).first()
