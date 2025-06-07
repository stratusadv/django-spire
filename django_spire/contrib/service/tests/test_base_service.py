from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.model_service import BaseModelService
from django_spire.contrib.service.tests.services import UserModelService



class TestBaseService(TestCase):
    def setUp(self):
        self.user = create_super_user()


    def test_abstraction_on_init(self):

        class BrokenModelService(BaseModelService):
            def create_taco(self):
                return "Taco!"

        with self.assertRaises(NotImplementedError) as context:
            BrokenModelService()

    def test_is_class_instance(self):
        service = UserModelService(self.user)
        self.assertTrue(service.obj_is_class_instance(User))
        self.assertFalse(service.obj_is_class_instance(self.user))

    def test_is_ready_instance(self):
        service = UserModelService(self.user)

        self.assertTrue(service.obj_is_ready_instance(self.user))
        self.assertFalse(service.obj_is_ready_instance(User))

    def test_is_new_instance(self):
        service = UserModelService(self.user)
        new_user = User()

        self.assertTrue(service.obj_is_new_instance(new_user))
        self.assertFalse(service.obj_is_new_instance(self.user))
