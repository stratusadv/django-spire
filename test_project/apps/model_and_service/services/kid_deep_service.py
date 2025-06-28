from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.model_and_service.models import Kid


class KidDeepService(BaseDjangoModelService):
    kid: Kid

    def postfix_deep_to_first_name(self):
        return f'{self.kid.first_name} deep'
