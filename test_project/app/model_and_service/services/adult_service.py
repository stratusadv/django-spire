from __future__ import annotations

from typing import TYPE_CHECKING
from django_spire.contrib.service.django_model_service import BaseDjangoModelService
from test_project.apps.model_and_service.services.adult_sub_service import AdultSubService

if TYPE_CHECKING:
    from test_project.apps.model_and_service.models import Adult


class AdultService(BaseDjangoModelService['Adult']):
    obj: Adult

    sub: AdultSubService = AdultSubService()

    def get_the_first_name(self, weather: str = ''):
        return self.obj.first_name + weather

    def set_inactive(self):
        self.obj.is_active = False
        self.obj.save()

    def find_all(self):
        return self.obj_class.objects.all()


