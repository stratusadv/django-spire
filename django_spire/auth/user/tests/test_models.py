from __future__ import annotations

import pytest

from django.db import IntegrityError

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
        assert AuthUser._meta.proxy

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
        assert AuthUser.objects.filter(pk=user.pk).exists()

    def test_user_update(self) -> None:
        self.user.first_name = 'Updated'
        self.user.save()
        self.user.refresh_from_db()
        assert self.user.first_name == 'Updated'

    def test_user_deletion(self) -> None:
        user_pk = self.user.pk
        self.user.delete()
        assert not AuthUser.objects.filter(pk=user_pk).exists()

    def test_user_email(self) -> None:
        assert self.user.email == 'test@example.com'

    def test_user_is_active_default(self) -> None:
        user = create_user(username='activeuser')
        assert user.is_active

    def test_user_is_active_false(self) -> None:
        user = create_user(username='inactiveuser', is_active=False)
        assert not user.is_active

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
        with pytest.raises(IntegrityError):
            AuthUser.objects.create(username='testuser')

    def test_user_password_hashing(self) -> None:
        user = create_user(username='passworduser')
        user.set_password('testpassword123')
        user.save()
        assert user.check_password('testpassword123')
        assert not user.check_password('wrongpassword')

    def test_user_last_login_initially_none(self) -> None:
        user = create_user(username='nologinuser')
        assert user.last_login is None

    def test_breadcrumbs_returns_breadcrumbs(self) -> None:
        crumbs = self.user.breadcrumbs()
        assert crumbs is not None

    def test_breadcrumbs_without_pk(self) -> None:
        unsaved_user = AuthUser(username='unsaved', first_name='Unsaved')
        crumbs = unsaved_user.breadcrumbs()
        assert crumbs is not None

    def test_breadcrumbs_contains_user_name(self) -> None:
        crumbs = self.user.breadcrumbs()
        names = [c.name for c in crumbs.data]
        assert 'Test User' in names

    def test_base_breadcrumb_returns_breadcrumbs(self) -> None:
        crumbs = AuthUser.base_breadcrumb()
        assert crumbs is not None

    def test_base_breadcrumb_contains_users(self) -> None:
        crumbs = AuthUser.base_breadcrumb()
        names = [c.name for c in crumbs.data]
        assert 'Users' in names

    def test_user_inheritance_from_django_user(self) -> None:
        from django.contrib.auth.models import User
        assert issubclass(AuthUser, User)

    def test_activity_mixin(self) -> None:
        assert hasattr(self.user, 'add_activity')

    def test_user_get_short_name(self) -> None:
        assert self.user.get_short_name() == 'Test'

    def test_user_str_representation(self) -> None:
        assert str(self.user) == 'testuser'

    def test_user_email_user(self) -> None:
        assert hasattr(self.user, 'email_user')

    def test_user_has_perm(self) -> None:
        assert hasattr(self.user, 'has_perm')

    def test_user_has_perms(self) -> None:
        assert hasattr(self.user, 'has_perms')

    def test_user_has_module_perms(self) -> None:
        assert hasattr(self.user, 'has_module_perms')

    def test_user_is_anonymous(self) -> None:
        assert not self.user.is_anonymous

    def test_user_is_authenticated(self) -> None:
        assert self.user.is_authenticated

    def test_user_date_joined(self) -> None:
        assert self.user.date_joined is not None

    def test_user_username_max_length(self) -> None:
        max_length = AuthUser._meta.get_field('username').max_length
        assert max_length == 150

    def test_user_first_name_max_length(self) -> None:
        max_length = AuthUser._meta.get_field('first_name').max_length
        assert max_length == 150

    def test_user_last_name_max_length(self) -> None:
        max_length = AuthUser._meta.get_field('last_name').max_length
        assert max_length == 150

    def test_user_email_max_length(self) -> None:
        max_length = AuthUser._meta.get_field('email').max_length
        assert max_length == 254

    def test_user_with_unicode_names(self) -> None:
        user = create_user(
            username='unicodeuser',
            first_name='Tëst',
            last_name='Üsér'
        )
        assert user.first_name == 'Tëst'
        assert user.last_name == 'Üsér'
        assert 'Tëst' in user.get_full_name()

    def test_user_refresh_from_db(self) -> None:
        original_name = self.user.first_name
        AuthUser.objects.filter(pk=self.user.pk).update(first_name='Changed')
        self.user.refresh_from_db()
        assert self.user.first_name == 'Changed'
        assert self.user.first_name != original_name

    def test_user_get_or_create(self) -> None:
        user, created = AuthUser.objects.get_or_create(
            username='getorcreate',
            defaults={'first_name': 'Get', 'last_name': 'OrCreate'}
        )
        assert created
        user2, created2 = AuthUser.objects.get_or_create(
            username='getorcreate',
            defaults={'first_name': 'Different', 'last_name': 'Name'}
        )
        assert not created2
        assert user.pk == user2.pk

    def test_user_exists(self) -> None:
        assert AuthUser.objects.filter(username='testuser').exists()
        assert not AuthUser.objects.filter(username='nonexistent').exists()

    def test_user_count(self) -> None:
        initial_count = AuthUser.objects.count()
        create_user(username='countuser1')
        create_user(username='countuser2')
        assert AuthUser.objects.count() == initial_count + 2

    def test_user_filter_by_is_active(self) -> None:
        create_user(username='active1', is_active=True)
        create_user(username='inactive1', is_active=False)
        active_users = AuthUser.objects.filter(is_active=True)
        inactive_users = AuthUser.objects.filter(is_active=False)
        assert active_users.filter(username='active1').exists()
        assert inactive_users.filter(username='inactive1').exists()

    def test_user_order_by_username(self) -> None:
        create_user(username='zebra')
        create_user(username='alpha')
        users = AuthUser.objects.order_by('username')
        usernames = list(users.values_list('username', flat=True))
        assert usernames == sorted(usernames)

    def test_user_permissions_relationship(self) -> None:
        assert hasattr(self.user, 'user_permissions')

    def test_user_set_unusable_password(self) -> None:
        self.user.set_unusable_password()
        assert not self.user.has_usable_password()

    def test_user_check_password_with_unusable(self) -> None:
        self.user.set_unusable_password()
        assert not self.user.check_password('anypassword')
