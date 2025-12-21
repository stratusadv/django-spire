from __future__ import annotations

from django.test import TestCase

from test_project.apps.model_and_service.models import Adult
from test_project.apps.model_and_service.tests.factories import create_adult
from test_project.apps.model_and_service.services.adult_service import AdultService


class TestBaseService(TestCase):
    def setUp(self):
        self.adult = create_adult()

    def test_get_sets_objects_dynamically(self):
        assert self.adult.services._obj_type == Adult

        assert self.adult.services.obj == self.adult

        assert Adult.services.obj.id is None

    def test_model_class_access(self):
        assert self.adult.services.obj_class is not None
        assert self.adult.services.obj_class == self.adult.__class__

    def test_model_class_service_method(self):
        assert self.adult.services.find_all() is not None

    def test_method_on_top_level_service(self):
        self.adult.services.set_inactive()
        assert not self.adult.is_active

    def test_obj_changes_cascade_to_sub_services(self):
        self.adult.services.set_inactive()
        assert not self.adult.is_active

        assert self.adult.services.sub.obj.is_active == self.adult.is_active

    def test_method_on_sub_service(self):
        assert self.adult.get_full_name() == self.adult.services.sub.full_name()

    def test_stand_alone_service(self):
        service = AdultService(self.adult)
        service.set_inactive()
        assert not self.adult.is_active

