from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.service import BaseService
from django_spire.contrib.service.tests.services import UserService



class TestBaseService(TestCase):
    def setUp(self):
        self.user = create_super_user()


    def test_init(self):
        class NewService(BaseService):
            obj_class = User
            obj_name = 'user'

        try:
            _ = NewService()
            _.user
            self.assertTrue(True)
        except:
            raise

    def test_abstraction_on_init(self):

        class BrokenService(BaseService):
            def create_taco(self):
                return "Taco!"

        with self.assertRaises(NotImplementedError) as context:
            BrokenService()

    def test_is_class_instance(self):
        service = UserService(self.user)
        self.assertTrue(service.is_class_instance(User))
        self.assertFalse(service.is_class_instance(self.user))

    def test_is_ready_instance(self):
        service = UserService(self.user)

        self.assertTrue(service.is_ready_instance(self.user))
        self.assertFalse(service.is_ready_instance(User))

    def test_is_new_instance(self):
        service = UserService(self.user)
        new_user = User()

        self.assertTrue(service.is_new_instance(new_user))
        self.assertFalse(service.is_new_instance(self.user))
