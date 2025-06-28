from __future__ import annotations

from typing import TYPE_CHECKING
from django_spire.contrib.service.django_model_service import BaseDjangoModelService
from test_project.apps.model_and_service.services.kid_sub_service import KidSubService

if TYPE_CHECKING:
    from test_project.apps.model_and_service.models import Kid


class KidService(BaseDjangoModelService):
    kid: Kid

    sub: KidSubService = KidSubService()

    def prepend_tacos_str_name(self) -> str:
        return f'tacos {self.kid.first_name} {self.kid.last_name}'
