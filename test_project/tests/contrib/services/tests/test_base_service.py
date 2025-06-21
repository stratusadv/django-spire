from django.test import TestCase

from test_project.apps.test_model.models import TestModel
from test_project.apps.test_model.tests.factories import create_test_model
from test_project.tests.contrib.services.tests.services import TestModelService


class TestBaseService(TestCase):
    def setUp(self):
        self.test_model = create_test_model()

    def test_get_sets_objects_dynamically(self):
        """
            When a service is accessed, __get__ does the following:
                1) Sets the obj name and type
                2) Initializes the first-class var to the target object
                3) Initializes all base services with the target object
        """
        self.assertEqual(self.test_model.services._obj_name, 'test_model')
        self.assertEqual(self.test_model.services._obj_type, TestModel)

        # Initializes first-class var to the accessed object
        self.assertEqual(self.test_model.services.test_model, self.test_model)

        # Initialize null object from model class.
        self.assertEqual(TestModel.services.test_model.id, None)

    def test_method_on_top_level_service(self):
        self.test_model.services.set_inactive()
        self.assertFalse(self.test_model.is_active)

    def test_obj_changes_cascade_to_sub_services(self):
        self.test_model.services.set_inactive()
        self.assertFalse(self.test_model.is_active)

        self.assertEqual(self.test_model.services.sub.test_model.is_active, self.test_model.is_active)

    def test_method_on_sub_service(self):
        self.assertEqual(self.test_model.get_full_name(), self.test_model.services.sub.full_name())

    def test_cache_instance_and_sub_services(self):
        # Cache key is added to the target object
        service = self.test_model.services
        self.assertTrue(hasattr(self.test_model, service.__class__._cache_key()))

    def test_stand_alone_service(self):
        service = TestModelService(self.test_model)
        service.set_inactive()
        self.assertFalse(self.test_model.is_active)

