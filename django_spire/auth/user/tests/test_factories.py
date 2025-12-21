from __future__ import annotations

from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_super_user, create_user
from django_spire.core.tests.test_cases import BaseTestCase


class CreateUserTestCase(BaseTestCase):
    def test_creates_user(self) -> None:
        user = create_user(username='testuser')
        assert isinstance(user, AuthUser)
        assert AuthUser.objects.filter(username='testuser').exists()

    def test_creates_user_with_username(self) -> None:
        user = create_user(username='myuser')
        assert user.username == 'myuser'

    def test_creates_user_with_kwargs(self) -> None:
        user = create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.email == 'test@example.com'

    def test_returns_existing_user_if_exists(self) -> None:
        user1 = create_user(username='existinguser')
        user2 = create_user(username='existinguser')
        assert user1.pk == user2.pk

    def test_get_or_create_behavior(self) -> None:
        user1 = create_user(username='getorcreate', first_name='First')
        user2 = create_user(username='getorcreate', first_name='Different')
        assert user1.pk == user2.pk
        assert user1.first_name == 'First'

    def test_creates_with_is_active_true(self) -> None:
        user = create_user(username='activeuser', is_active=True)
        assert user.is_active

    def test_creates_with_is_active_false(self) -> None:
        user = create_user(username='inactiveuser', is_active=False)
        assert not user.is_active

    def test_user_has_pk(self) -> None:
        user = create_user(username='pkuser')
        assert user.pk is not None

    def test_creates_unique_users(self) -> None:
        user1 = create_user(username='user1')
        user2 = create_user(username='user2')
        assert user1.pk != user2.pk

    def test_creates_with_unicode_username(self) -> None:
        user = create_user(username='tëstüsér')
        assert user.username == 'tëstüsér'

    def test_creates_with_email(self) -> None:
        user = create_user(username='emailuser', email='email@example.com')
        assert user.email == 'email@example.com'

    def test_creates_with_empty_email(self) -> None:
        user = create_user(username='noemail', email='')
        assert user.email == ''

    def test_creates_with_staff_status(self) -> None:
        user = create_user(username='staffuser', is_staff=True)
        assert user.is_staff

    def test_creates_without_staff_status(self) -> None:
        user = create_user(username='nonstaffuser', is_staff=False)
        assert not user.is_staff

    def test_creates_with_superuser_status(self) -> None:
        user = create_user(username='superuser', is_superuser=True)
        assert user.is_superuser

    def test_creates_without_superuser_status(self) -> None:
        user = create_user(username='normaluser', is_superuser=False)
        assert not user.is_superuser

    def test_user_is_persisted(self) -> None:
        user = create_user(username='persisteduser')
        assert AuthUser.objects.filter(pk=user.pk).exists()

    def test_creates_with_long_username(self) -> None:
        long_username = 'a' * 150
        user = create_user(username=long_username)
        assert user.username == long_username

    def test_creates_with_special_characters_username(self) -> None:
        user = create_user(username='test.user@example.com')
        assert user.username == 'test.user@example.com'


class CreateSuperUserTestCase(BaseTestCase):
    def test_creates_superuser(self) -> None:
        user = create_super_user()
        assert isinstance(user, AuthUser)
        assert user.is_superuser

    def test_superuser_is_staff(self) -> None:
        user = create_super_user()
        assert user.is_staff

    def test_superuser_default_username(self) -> None:
        user = create_super_user()
        assert user.username == 'stratus'

    def test_superuser_default_email(self) -> None:
        user = create_super_user()
        assert user.email == 'bobert@stratusadv.com'

    def test_superuser_default_names(self) -> None:
        user = create_super_user()
        assert user.first_name == 'Bob'
        assert user.last_name == 'Robertson'

    def test_superuser_default_password(self) -> None:
        user = create_super_user()
        assert user.check_password('stratus')

    def test_superuser_custom_password(self) -> None:
        user = create_super_user(password='custompassword')  # noqa: S106
        assert user.check_password('custompassword')

    def test_superuser_returns_existing(self) -> None:
        user1 = create_super_user()
        user2 = create_super_user()
        assert user1.pk == user2.pk

    def test_superuser_has_pk(self) -> None:
        user = create_super_user()
        assert user.pk is not None

    def test_superuser_is_active(self) -> None:
        user = create_super_user()
        assert user.is_active

    def test_superuser_has_all_permissions(self) -> None:
        user = create_super_user()
        assert user.has_perm('any.permission')

    def test_superuser_with_custom_kwargs(self) -> None:
        user = create_super_user(first_name='Custom', last_name='Name')
        assert user.first_name in ('Bob', 'Custom')

    def test_superuser_is_persisted(self) -> None:
        user = create_super_user()
        assert AuthUser.objects.filter(pk=user.pk).exists()

    def test_superuser_can_authenticate(self) -> None:
        user = create_super_user()
        assert user.check_password('stratus')

    def test_superuser_password_is_hashed(self) -> None:
        user = create_super_user()
        assert user.password != 'stratus'  # noqa: S105

    def test_multiple_calls_same_user(self) -> None:
        users = [create_super_user() for _ in range(5)]
        pks = [u.pk for u in users]
        assert len(set(pks)) == 1

    def test_superuser_get_full_name(self) -> None:
        user = create_super_user()
        full_name = user.get_full_name()
        assert 'Bob' in full_name or 'Robertson' in full_name
