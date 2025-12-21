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

    def test_get_concrete_fields_returns_dict(self) -> None:
        service = UserService(self.user)

        result = service._get_concrete_fields()

        assert isinstance(result, dict)
        assert 'username' in result
        assert 'email' in result

    def test_get_touched_fields_returns_list(self) -> None:
        service = UserService(self.user)
        concrete_fields = service._get_concrete_fields()

        result = service._get_touched_fields(concrete_fields, username='newuser')

        assert isinstance(result, list)

    def test_get_touched_fields_sets_attribute(self) -> None:
        service = UserService(self.user)
        concrete_fields = service._get_concrete_fields()

        service._get_touched_fields(concrete_fields, first_name='NewName')

        assert service.obj.first_name == 'NewName'

    def test_get_touched_fields_logs_warning_for_invalid_field(self) -> None:
        service = UserService(self.user)
        concrete_fields = service._get_concrete_fields()

        with patch('django_spire.contrib.service.django_model_service.log') as mock_log:
            service._get_touched_fields(concrete_fields, invalid_field='value')

            mock_log.warning.assert_called_once()

    def test_get_touched_fields_skips_auto_created_fields(self) -> None:
        service = UserService(self.user)
        concrete_fields = service._get_concrete_fields()

        result = service._get_touched_fields(concrete_fields, id=999)

        assert 'id' not in result

    def test_has_get_concrete_fields_method(self) -> None:
        assert hasattr(BaseDjangoModelService, '_get_concrete_fields')

    def test_has_get_touched_fields_method(self) -> None:
        assert hasattr(BaseDjangoModelService, '_get_touched_fields')

    def test_has_save_model_obj_method(self) -> None:
        assert hasattr(BaseDjangoModelService, 'save_model_obj')

    def test_has_validate_model_obj_method(self) -> None:
        assert hasattr(BaseDjangoModelService, 'validate_model_obj')

    def test_save_model_obj_raises_error_without_field_data(self) -> None:
        service = UserService(self.user)

        with pytest.raises(ServiceError, match='Field data is required'):
            service.save_model_obj()

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

    def test_save_model_obj_logs_warning_when_no_changes(self) -> None:
        service = UserService(self.user)

        with patch('django_spire.contrib.service.django_model_service.log') as mock_log:
            service.save_model_obj(id=self.user.id)

            mock_log.warning.assert_called_once()

    def test_validate_model_obj_returns_touched_fields(self) -> None:
        service = UserService(self.user)

        result = service.validate_model_obj(first_name='Valid')

        assert isinstance(result, list)
        assert 'first_name' in result

    def test_validate_model_obj_raises_validation_error(self) -> None:
        service = UserService(self.user)

        with pytest.raises(ValidationError):
            service.validate_model_obj(email='invalid-email')
