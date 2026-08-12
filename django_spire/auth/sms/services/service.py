from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.sms.services.processor_service import AuthSmsProcessorService
from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.auth.sms.models import AuthSms


class AuthSmsService(BaseDjangoModelService['AuthSms']):
    obj: AuthSms

    processor = AuthSmsProcessorService()
