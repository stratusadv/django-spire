from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from test_project.apps.model_and_service.services.kid_deep_service import KidDeepService

if TYPE_CHECKING:
    from test_project.apps.model_and_service.models import Kid


class KidSubService(BaseDjangoModelService):
    kid: Kid

    deep: KidDeepService = KidDeepService()

    def full_name(self):
        return f'{self.kid.first_name} {self.kid.last_name}'
