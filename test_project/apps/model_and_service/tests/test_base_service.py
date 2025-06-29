from django.test import TestCase

from test_project.apps.model_and_service.models import Adult
from test_project.apps.model_and_service.tests.factories import create_adult
from test_project.apps.model_and_service.services.adult_service import AdultService


class TestBaseService(TestCase):
    def setUp(self):
        self.adult = create_adult()

    def test_get_sets_objects_dynamically(self):
        self.assertEqual(self.adult.services._obj_name, 'adult')
        self.assertEqual(self.adult.services._obj_type, Adult)

        self.assertEqual(self.adult.services.adult, self.adult)

        self.assertEqual(Adult.services.adult.id, None)

    def test_model_class_access(self):
        self.assertIsNotNone(self.adult.services.Adult)
        self.assertEqual(self.adult.services.Adult, self.adult.__class__)

    def test_model_class_service_method(self):
        self.assertIsNotNone(self.adult.services.find_all())

    def test_method_on_top_level_service(self):
        self.adult.services.set_inactive()
        self.assertFalse(self.adult.is_active)

    def test_obj_changes_cascade_to_sub_services(self):
        self.adult.services.set_inactive()
        self.assertFalse(self.adult.is_active)

        self.assertEqual(self.adult.services.sub.adult.is_active, self.adult.is_active)

    def test_method_on_sub_service(self):
        self.assertEqual(self.adult.get_full_name(), self.adult.services.sub.full_name())

    def test_stand_alone_service(self):
        service = AdultService(self.adult)
        service.set_inactive()
        self.assertFalse(self.adult.is_active)

