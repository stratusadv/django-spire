from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class AuthUserModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )

    def test_meta_proxy(self) -> None:
        assert AuthUser._meta.proxy is True

    def test_meta_verbose_name(self) -> None:
        assert AuthUser._meta.verbose_name == 'Auth User'
        assert AuthUser._meta.verbose_name_plural == 'Auth Users'

    def test_get_full_name(self) -> None:
        assert self.user.get_full_name() == 'Test User'

    def test_get_full_name_first_only(self) -> None:
        user = create_user(username='firstonly', first_name='First', last_name='')
        assert 'First' in user.get_full_name()

    def test_get_full_name_last_only(self) -> None:
        user = create_user(username='lastonly', first_name='', last_name='Last')
        assert 'Last' in user.get_full_name()

    def test_get_full_name_empty(self) -> None:
        user = create_user(username='noname', first_name='', last_name='')
        assert user.get_full_name() == ''

    def test_services_class_attribute(self) -> None:
        assert AuthUser.services is not None

    def test_user_creation(self) -> None:
        user = create_user(
            username='newuser',
            first_name='New',
            last_name='User',
            email='new@example.com'
        )
        assert user.pk is not None
        assert AuthUser.objects.filter(pk=user.pk).exists() is True

    def test_user_update(self) -> None:
        self.user.first_name = 'Updated'
        self.user.save()
        self.user.refresh_from_db()
        assert self.user.first_name == 'Updated'

    def test_user_deletion(self) -> None:
        user_pk = self.user.pk
        self.user.delete()
        assert AuthUser.objects.filter(pk=user_pk).exists() is False

    def test_user_email(self) -> None:
        assert self.user.email == 'test@example.com'

    def test_user_is_active_default(self) -> None:
        user = create_user(username='activeuser')
        assert user.is_active is True

    def test_user_is_active_false(self) -> None:
        user = create_user(username='inactiveuser', is_active=False)
        assert user.is_active is False

    def test_user_groups_relationship(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user.groups.add(group)
        assert group in self.user.groups.all()

    def test_user_multiple_groups(self) -> None:
        group1 = AuthGroup.objects.create(name='Group 1')
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user.groups.add(group1, group2)
        assert self.user.groups.count() == 2

    def test_user_remove_from_group(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user.groups.add(group)
        self.user.groups.remove(group)
        assert group not in self.user.groups.all()

    def test_user_clear_groups(self) -> None:
        group1 = AuthGroup.objects.create(name='Group 1')
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user.groups.add(group1, group2)
        self.user.groups.clear()
        assert self.user.groups.count() == 0

    def test_user_username_unique(self) -> None:
        from django.db import IntegrityError
        import pytest
        with pytest.raises(IntegrityError):
            AuthUser.objects.create(username='testuser')

    def test_user_password_hashing(self) -> None:
        user = create_user(username='passworduser')
        user.set_password('testpassword123')
        user.save()
        assert user.check_password('testpassword123') is True
        assert user.check_password('wrongpassword') is False

    def test_user_last_login_initially_none(self) -> None:
        user = create_user(username='nologinuser')
        assert user.last_login is None
