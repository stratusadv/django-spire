from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.exceptions import ServiceException
from django_spire.contrib.service.model_service import BaseModelService
from django_spire.contrib.service.tests.services import UserModelService



class TestBaseService(TestCase):
    def setUp(self):
        User.services = UserModelService()

        self.user = create_super_user()

    def tearDown(self):
        User.services = None

    def test_abstraction_on_init(self):
        class BrokenModelService(BaseModelService):
            def create_taco(self):
                return "Taco!"

        with self.assertRaises(ValueError) as context:
            BrokenModelService()

    def test_is_ready_instance(self):
        self.assertTrue(self.user.services.obj_is_ready_instance)
        self.assertFalse(User().services.obj_is_ready_instance)

    def test_is_new_instance(self):
        new_user = User()

        self.assertTrue(new_user.services.obj_is_new_instance)
        self.assertFalse(self.user.services.obj_is_new_instance)
