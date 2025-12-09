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
        assert form.is_valid()

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
        assert form.is_valid()
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
        assert form.is_valid()

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
        assert form.is_valid()

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
        assert not form.is_valid()
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
        assert form.is_valid()

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
        assert form.is_valid()
        user = form.save()
        assert not user.is_active

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
        assert form.is_valid()

    def test_form_fields(self) -> None:
        form = UserForm()
        assert 'first_name' in form.fields
        assert 'last_name' in form.fields
        assert 'email' in form.fields
        assert 'is_active' in form.fields

    def test_form_excludes_password(self) -> None:
        form = UserForm()
        assert 'password' not in form.fields

    def test_form_excludes_username(self) -> None:
        form = UserForm()
        assert 'username' not in form.fields

    def test_save_preserves_password(self) -> None:
        self.user.set_password('originalpassword')
        self.user.save()
        form = UserForm(
            data={
                'first_name': 'Updated',
                'last_name': 'User',
                'email': 'updated@example.com',
                'is_active': True
            },
            instance=self.user
        )
        form.is_valid()
        user = form.save()
        assert user.check_password('originalpassword')

    def test_email_with_plus_sign(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test+alias@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()

    def test_long_first_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'A' * 150,
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()

    def test_long_last_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'A' * 150,
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()

    def test_first_name_with_hyphen(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Mary-Jane',
                'last_name': 'Watson',
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()

    def test_last_name_with_apostrophe(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Patrick',
                'last_name': "O'Brien",
                'email': 'test@example.com',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()

    def test_email_case_preserved(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'Test@Example.COM',
                'is_active': True
            },
            instance=self.user
        )
        assert form.is_valid()
        user = form.save()
        assert user.username == 'Test@Example.COM'


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
        assert form.is_valid()

    def test_password_too_short(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'short'
            }
        )
        assert not form.is_valid()
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
        assert form.is_valid()

    def test_password_seven_characters(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': '1234567'
            }
        )
        assert not form.is_valid()

    def test_save_creates_user(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid()
        user = form.save()
        assert isinstance(user, AuthUser)
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
        assert form.is_valid()
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
        assert form.is_valid()

    def test_empty_last_name(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': '',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid()

    def test_invalid_email_format(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'invalid-email',
                'password': 'securepassword123'
            }
        )
        assert not form.is_valid()

    def test_empty_email(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': '',
                'password': 'securepassword123'
            }
        )
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_empty_password(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': ''
            }
        )
        assert not form.is_valid()

    def test_password_with_spaces(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'pass word 123'
            }
        )
        assert form.is_valid()

    def test_long_password(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'a' * 100
            }
        )
        assert form.is_valid()

    def test_created_user_can_authenticate(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid()
        user = form.save()
        assert user.check_password('securepassword123')

    def test_password_error_message(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'short'
            }
        )
        form.is_valid()
        assert '8 characters' in form.errors['password'][0]

    def test_form_fields(self) -> None:
        form = RegisterUserForm()
        assert 'first_name' in form.fields
        assert 'last_name' in form.fields
        assert 'email' in form.fields
        assert 'password' in form.fields

    def test_password_with_special_characters(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'P@ssw0rd!#$%'
            }
        )
        assert form.is_valid()

    def test_password_with_unicode(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'pässwörd日本語'
            }
        )
        assert form.is_valid()

    def test_unicode_names(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'Tëst',
                'last_name': 'Üsér',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        assert form.is_valid()
        user = form.save()
        assert user.first_name == 'Tëst'
        assert user.last_name == 'Üsér'

    def test_user_is_active_after_registration(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        form.is_valid()
        user = form.save()
        assert user.is_active

    def test_user_is_not_staff_after_registration(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        form.is_valid()
        user = form.save()
        assert not user.is_staff

    def test_user_is_not_superuser_after_registration(self) -> None:
        form = RegisterUserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }
        )
        form.is_valid()
        user = form.save()
        assert not user.is_superuser


class UserGroupFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group1 = AuthGroup.objects.create(name='Group 1')
        self.group2 = AuthGroup.objects.create(name='Group 2')
        self.group3 = AuthGroup.objects.create(name='Group 3')

    def test_valid_form(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group2.pk]})
        assert form.is_valid()

    def test_cleaned_data_contains_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk]})
        assert form.is_valid()
        assert self.group1 in form.cleaned_data['group_list']

    def test_single_group(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['group_list']) == 1

    def test_multiple_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group2.pk, self.group3.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['group_list']) == 3

    def test_invalid_group_id(self) -> None:
        form = UserGroupForm(data={'group_list': [99999]})
        assert not form.is_valid()

    def test_mixed_valid_invalid_groups(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, 99999]})
        assert not form.is_valid()

    def test_empty_group_list_fails(self) -> None:
        form = UserGroupForm(data={'group_list': []})
        assert not form.is_valid()

    def test_no_data_fails(self) -> None:
        form = UserGroupForm(data={})
        assert not form.is_valid()

    def test_duplicate_group_ids(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['group_list']) == 1

    def test_negative_group_id(self) -> None:
        form = UserGroupForm(data={'group_list': [-1]})
        assert not form.is_valid()

    def test_zero_group_id(self) -> None:
        form = UserGroupForm(data={'group_list': [0]})
        assert not form.is_valid()

    def test_string_group_id(self) -> None:
        form = UserGroupForm(data={'group_list': ['invalid']})
        assert not form.is_valid()

    def test_form_queryset(self) -> None:
        form = UserGroupForm()
        queryset = form.fields['group_list'].queryset
        assert self.group1 in queryset
        assert self.group2 in queryset
        assert self.group3 in queryset

    def test_all_groups_selectable(self) -> None:
        form = UserGroupForm(data={'group_list': [self.group1.pk, self.group2.pk, self.group3.pk]})
        assert form.is_valid()
        groups = form.cleaned_data['group_list']
        assert self.group1 in groups
        assert self.group2 in groups
        assert self.group3 in groups

    def test_group_list_field_required(self) -> None:
        form = UserGroupForm()
        assert form.fields['group_list'].required

    def test_form_with_deleted_group(self) -> None:
        group_pk = self.group3.pk
        self.group3.delete()
        form = UserGroupForm(data={'group_list': [group_pk]})
        assert not form.is_valid()
