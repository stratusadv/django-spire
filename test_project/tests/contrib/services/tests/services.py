from __future__ import annotations

from typing import TYPE_CHECKING
from django_spire.contrib.service.django_model_service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.apps.test_model.models import TestModel, TestModelChild


class TestModelSubService(BaseDjangoModelService):
    test_model: TestModel

    def full_name(self):
        return self.test_model.get_full_name()


class TestModelChildSubService(BaseDjangoModelService):
    test_model_child: TestModelChild

    def full_name(self):
        return f'{self.test_model_child.first_name} {self.test_model_child.last_name}'


class TestModelService(BaseDjangoModelService):
    test_model: TestModel
    sub: TestModelService = TestModelSubService

    def get_the_first_name(self, weather: str = ''):
        return self.test_model.first_name + weather

    def set_inactive(self):
        self.test_model.is_active = False
        self.test_model.save()


class TestModelChildService(BaseDjangoModelService):
    test_model_child: TestModelChild