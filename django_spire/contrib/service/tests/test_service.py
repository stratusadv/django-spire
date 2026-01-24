from __future__ import annotations

import pytest

from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from django_spire.contrib.service import BaseDjangoModelService, ServiceError


class UserService(BaseDjangoModelService[User]):
    obj: User


class TestServiceError(TestCase):
    def test_can_be_raised(self) -> None:
        with pytest.raises(ServiceError):
            message = 'Test'
            raise ServiceError(message)

    def test_is_exception(self) -> None:
        assert issubclass(ServiceError, Exception)

    def test_message(self) -> None:
        error = ServiceError('Test error message')

        assert str(error) == 'Test error message'


class TestBaseDjangoModelService(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )

    def test_set_non_m2m_fields_sets_attribute(self) -> None:
        service = UserService(self.user)
        service._set_non_m2m_fields(first_name='NewName')

        assert service.obj.first_name == 'NewName'

    def test_set_non_m2m_fields_skips_auto_created_fields(self) -> None:
        UserService(self.user)._set_non_m2m_fields(id=999)

        assert self.user.id != 999

    def test_has_set_non_m2m_fields_method(self) -> None:
        assert hasattr(BaseDjangoModelService, '_set_non_m2m_fields')

    def test_has_set_m2m_fields_method(self) -> None:
        assert hasattr(BaseDjangoModelService, '_set_m2m_fields')

    def test_has_save_model_obj_method(self) -> None:
        assert hasattr(BaseDjangoModelService, 'save_model_obj')

    def test_save_model_obj_returns_tuple(self) -> None:
        service = UserService(self.user)

        result = service.save_model_obj(first_name='Updated')

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_save_model_obj_returns_model_and_bool(self) -> None:
        service = UserService(self.user)

        obj, created = service.save_model_obj(first_name='Updated')

        assert isinstance(obj, User)
        assert isinstance(created, bool)

    def test_save_model_obj_updates_existing_model(self) -> None:
        service = UserService(self.user)

        obj, created = service.save_model_obj(first_name='UpdatedName')

        assert created is False
        assert obj.first_name == 'UpdatedName'

    def test_save_model_obj_creates_new_model(self) -> None:
        new_user = User(username='newuser', email='new@test.com')
        service = UserService(new_user)

        obj, created = service.save_model_obj(username='newuser', email='new@test.com')

        assert created is True
        assert obj.pk is not None

    def test_save_model_updates_obj_with_previous_changes(self) -> None:
        service = UserService(self.user)

        service.obj.first_name = 'new_test'

        service.save_model_obj(id=self.user.id)

        assert service.obj.first_name == 'new_test'