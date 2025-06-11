from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.exceptions import ServiceException
from django_spire.contrib.service.django_model_service import BaseDjangoModelService
from django_spire.contrib.service.tests.services import TestUserModelService


class TestBaseService(TestCase):
    def setUp(self):
        User.services = TestUserModelService()

        self.user = create_super_user()

    def tearDown(self):
        User.services = None

    def test_abstraction_on_init(self):
        with self.assertRaises(ServiceException) as context:
            class BrokenModelService(BaseDjangoModelService):
                def create_taco(self):
                    return "Taco!"

            User.services = BrokenModelService()

            self.user.services.create_taco()

    def test_model_obj_is_created(self):
        self.assertTrue(self.user.services.model_obj_is_created)
        self.assertFalse(User().services.model_obj_is_created)

    def test_model_obj_is_new(self):
        new_user = User()

        self.assertTrue(new_user.services.model_obj_is_new)
        self.assertFalse(self.user.services.model_obj_is_new)
