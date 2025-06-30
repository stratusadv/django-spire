from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.model_and_service.models import Adult


class AdultSubService(BaseDjangoModelService['Adult']):
    obj: Adult

    def full_name(self):
        return self.obj.get_full_name()
