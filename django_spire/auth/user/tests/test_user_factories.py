from __future__ import annotations

from django_spire.auth.user.factories import register_new_user
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase


class RegisterNewUserTestCase(BaseTestCase):
    def test_creates_user(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert isinstance(user, AuthUser) is True
        assert AuthUser.objects.filter(pk=user.pk).exists() is True

    def test_sets_correct_attributes(self) -> None:
        user = register_new_user(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='securepassword123'
        )
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.email == 'john.doe@example.com'

    def test_username_is_lowercase_email(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='Test.User@Example.COM',
            password='securepassword123'
        )
        assert user.username == 'test.user@example.com'
        assert user.email == 'test.user@example.com'

    def test_password_is_set(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.check_password('securepassword123') is True

    def test_password_is_hashed(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.password != 'securepassword123'

    def test_user_is_active_by_default(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.is_active is True

    def test_user_is_not_staff_by_default(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.is_staff is False

    def test_user_is_not_superuser_by_default(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.is_superuser is False

    def test_empty_first_name(self) -> None:
        user = register_new_user(
            first_name='',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.first_name == ''

    def test_empty_last_name(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.last_name == ''

    def test_unicode_names(self) -> None:
        user = register_new_user(
            first_name='Tëst',
            last_name='Üser',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.first_name == 'Tëst'
        assert user.last_name == 'Üser'

    def test_long_password(self) -> None:
        long_password = 'a' * 100
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password=long_password
        )
        assert user.check_password(long_password) is True

    def test_special_characters_in_email(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test+special@example.com',
            password='securepassword123'
        )
        assert user.email == 'test+special@example.com'

    def test_wrong_password_fails(self) -> None:
        user = register_new_user(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123'
        )
        assert user.check_password('wrongpassword') is False
