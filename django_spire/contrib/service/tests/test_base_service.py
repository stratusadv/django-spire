from django.test import TestCase

from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.tests.factories import TestFakeUserModel


class TestBaseService(TestCase):
    def setUp(self):
        self.super_user = create_super_user()
        self.user = TestFakeUserModel.objects.first()

    def test_get_sets_objects_dynamically(self):
        """
            When a service is accessed, __get__ does the following:
                1) Sets the obj name and type
                2) Initializes the first-class var to the target object
                3) Initializes all base services with the target object
        """
        self.assertEqual(self.user.services._obj_name, 'user')
        self.assertEqual(self.user.services._obj_type, TestFakeUserModel)

        # Initializes first-class var to the accessed object
        self.assertEqual(self.user.services.user, self.user)

        # Initialize null object from model class.
        self.assertEqual(TestFakeUserModel.services.user.id, None)

    def test_method_on_top_level_service(self):
        self.user.services.set_inactive()
        self.assertFalse(self.user.is_active)

    def test_obj_changes_cascade_to_sub_services(self):
        self.user.services.set_inactive()
        self.assertFalse(self.user.is_active)

        self.assertEqual(self.user.services.sub.user.is_active, self.user.is_active)

    def test_method_on_sub_service(self):
        self.assertEqual(self.user.get_full_name(), self.user.services.sub.full_name())






