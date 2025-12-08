from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.forms import RegisterUserForm, UserForm, UserGroupForm
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class UserFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )

    def test_valid_form(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True

    def test_save_updates_username_to_email(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'newemail@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True
        user = form.save()
        assert user.username == 'newemail@example.com'

    def test_empty_first_name(self) -> None:
        form = UserForm(
            data={
                'first_name': '',
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True

    def test_empty_last_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': '',
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True

    def test_invalid_email(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'not-an-email',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is False
        assert 'email' in form.errors

    def test_empty_email(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': '',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True

    def test_is_active_false(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': False
            },
            instance=self.user
        )
        assert form.is_valid() is True
        user = form.save()
        assert user.is_active is False

    def test_unicode_names(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Tëst',
                'last_name': 'Üser',
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid() is True


class RegisterUserFormTestCase(BaseTestCase):
    def test_valid_form(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True

    def test_password_too_short(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'short'
            }
        )
        assert form.is_valid() is False
        assert 'password' in form.errors

    def test_password_exactly_eight_characters(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': '12345678'
            }
        )
        assert form.is_valid() is True

    def test_password_seven_characters(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': '1234567'
            }
        )
        assert form.is_valid() is False

    def test_save_creates_user(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True
        user = form.save()
        assert isinstance(user, AuthUser) is True
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.email == 'newuser@example.com'
        assert user.username == 'newuser@example.com'

    def test_email_saved_lowercase(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'NewUser@Example.COM',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True
        user = form.save()
        assert user.email == 'newuser@example.com'
        assert user.username == 'newuser@example.com'

    def test_empty_first_name(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': '',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True

    def test_empty_last_name(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': '',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True

    def test_invalid_email_format(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'invalid-email',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is False

    def test_empty_email(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': '',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True

    def test_empty_password(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': ''
            }
        )
        assert form.is_valid() is False

    def test_password_with_spaces(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'pass word 123'
            }
        )
        assert form.is_valid() is True

    def test_long_password(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'a' * 100
            }
        )
        assert form.is_valid() is True

    def test_created_user_can_authenticate(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid() is True
        user = form.save()
        assert user.check_password('securepassword123') is True


class UserGroupFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group1 = AuthGroup.objects.create(name='Group 1')
        self.group2 = AuthGroup.objects.create(name='Group 2')
        self.group3 = AuthGroup.objects.create(name='Group 3')

    def test_valid_form(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group2.pk]})
        assert form.is_valid() is True

    def test_cleaned_data_contains_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk]})
        assert form.is_valid() is True
        assert self.group1 in form.cleaned_data['group_list']

    def test_single_group(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk]})
        assert form.is_valid() is True
        assert len(form.cleaned_data['group_list']) == 1

    def test_multiple_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group2.pk, self.group3.pk]})
        assert form.is_valid() is True
        assert len(form.cleaned_data['group_list']) == 3

    def test_invalid_group_id(self) -> None:
        form = UserGroupForm(data={'group_list': [99999]})
        assert form.is_valid() is False

    def test_mixed_valid_invalid_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, 99999]})
        assert form.is_valid() is False

    def test_empty_group_list_fails(self) -> None:
        form = UserGroupForm(data={'group_list': []})
        assert form.is_valid() is False

    def test_no_data_fails(self) -> None:
        form = UserGroupForm(data={})
        assert form.is_valid() is False
