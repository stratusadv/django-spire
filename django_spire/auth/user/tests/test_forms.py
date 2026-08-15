from __future__ import annotations

from django.test import RequestFactory

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.forms import UserForm, UserGroupForm
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class UserFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = create_user(
            username='testuser', first_name='Test', last_name='User', email='test@example.com'
        )

    def test_valid_form(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_save_model_obj_updates_username_to_email(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'newemail@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()
        user = self.user.services.save_model_obj(self.super_user, **form.cleaned_data)
        assert user.username == 'newemail@example.com'

    def test_empty_first_name(self) -> None:
        form = UserForm(
            data={
                'first_name': '',
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_empty_last_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': '',
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_invalid_email(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'not-an-email',
                'is_active': True,
            },
            instance=self.user,
        )
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_empty_email(self) -> None:
        form = UserForm(
            data={'first_name': 'Test', 'last_name': 'User', 'email': '', 'is_active': True},
            instance=self.user,
        )
        assert form.is_valid()

    def test_is_active_false(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': False,
            },
            instance=self.user,
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
                'is_active': True,
            },
            instance=self.user,
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
                'is_active': True,
            },
            instance=self.user,
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
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_long_first_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'A' * 150,
                'last_name': 'User',
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_long_last_name(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'A' * 150,
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_first_name_with_hyphen(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Mary-Jane',
                'last_name': 'Watson',
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_last_name_with_apostrophe(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Patrick',
                'last_name': "O'Brien",
                'email': 'test@example.com',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()

    def test_email_case_preserved(self) -> None:
        form = UserForm(
            data={
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'Test@Example.COM',
                'is_active': True,
            },
            instance=self.user,
        )
        assert form.is_valid()
        user = self.user.services.save_model_obj(self.super_user, **form.cleaned_data)
        assert user.email == 'Test@Example.COM'
        assert user.username == 'Test@Example.COM'


class UserFormSaveModelObjTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.request = RequestFactory().post('/')
        self.request.user = self.super_user

    def test_save_model_obj_creates_user(self) -> None:
        form = UserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'newuser@example.com',
                'is_active': True,
            }
        )
        response = form.save_model_obj(self.request)

        user = AuthUser.objects.get(email='newuser@example.com')
        assert user.username == 'newuser@example.com'
        assert str(user.pk) in response.result['redirect']['url']

    def test_save_model_obj_updates_user(self) -> None:
        user = create_user(
            username='testuser', first_name='Test', last_name='User', email='test@example.com'
        )
        form = UserForm(
            data={
                'first_name': 'Updated',
                'last_name': 'Name',
                'email': 'updated@example.com',
                'is_active': True,
            },
            instance=user,
        )
        form.save_model_obj(self.request)

        user.refresh_from_db()
        assert user.first_name == 'Updated'
        assert user.email == 'updated@example.com'

    def test_save_model_obj_invalid_email_returns_error(self) -> None:
        form = UserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'invalid-email',
                'is_active': True,
            }
        )
        response = form.save_model_obj(self.request)

        assert response.result is None
        assert not AuthUser.objects.filter(first_name='New').exists()

    def test_save_model_obj_duplicate_email_returns_error(self) -> None:
        create_user(username='taken', email='taken@example.com')

        form = UserForm(
            data={
                'first_name': 'New',
                'last_name': 'User',
                'email': 'taken@example.com',
                'is_active': True,
            }
        )
        response = form.save_model_obj(self.request)

        assert response.result is None
        assert AuthUser.objects.filter(email='taken@example.com').count() == 1


class UserGroupFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group1 = AuthGroup.objects.create(name='Group 1')
        self.group2 = AuthGroup.objects.create(name='Group 2')
        self.group3 = AuthGroup.objects.create(name='Group 3')

    def test_valid_form(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk, self.group2.pk]})
        assert form.is_valid()

    def test_cleaned_data_contains_groups(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk]})
        assert form.is_valid()
        assert self.group1 in form.cleaned_data['groups']

    def test_single_group(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 1

    def test_multiple_groups(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk, self.group2.pk, self.group3.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 3

    def test_invalid_group_id(self) -> None:
        form = UserGroupForm(data={'groups': [99999]})
        assert not form.is_valid()

    def test_mixed_valid_invalid_groups(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk, 99999]})
        assert not form.is_valid()

    def test_empty_group_list_clears_groups(self) -> None:
        form = UserGroupForm(data={'groups': []})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 0

    def test_no_data_clears_groups(self) -> None:
        form = UserGroupForm(data={})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 0

    def test_duplicate_group_ids(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk, self.group1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 1

    def test_negative_group_id(self) -> None:
        form = UserGroupForm(data={'groups': [-1]})
        assert not form.is_valid()

    def test_zero_group_id(self) -> None:
        form = UserGroupForm(data={'groups': [0]})
        assert not form.is_valid()

    def test_string_group_id(self) -> None:
        form = UserGroupForm(data={'groups': ['invalid']})
        assert not form.is_valid()

    def test_form_queryset(self) -> None:
        form = UserGroupForm()
        queryset = form.fields['groups'].queryset
        assert self.group1 in queryset
        assert self.group2 in queryset
        assert self.group3 in queryset

    def test_all_groups_selectable(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk, self.group2.pk, self.group3.pk]})
        assert form.is_valid()
        groups = form.cleaned_data['groups']
        assert self.group1 in groups
        assert self.group2 in groups
        assert self.group3 in groups

    def test_groups_field_is_not_required(self) -> None:
        form = UserGroupForm()
        assert not form.fields['groups'].required

    def test_form_with_deleted_group(self) -> None:
        group_pk = self.group3.pk
        self.group3.delete()
        form = UserGroupForm(data={'groups': [group_pk]})
        assert not form.is_valid()


class UserGroupFormSaveModelObjTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = create_user(
            username='testuser', first_name='Test', last_name='User', email='test@example.com'
        )
        self.group1 = AuthGroup.objects.create(name='Group 1')
        self.group2 = AuthGroup.objects.create(name='Group 2')

        self.request = RequestFactory().post('/')
        self.request.user = self.super_user

    def test_save_model_obj_sets_single_group(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk]}, instance=self.user)
        form.save_model_obj(self.request)

        self.user.refresh_from_db()
        assert self.group1 in self.user.groups.all()

    def test_save_model_obj_sets_multiple_groups(self) -> None:
        form = UserGroupForm(
            data={'groups': [self.group1.pk, self.group2.pk]}, instance=self.user
        )
        form.save_model_obj(self.request)

        self.user.refresh_from_db()
        assert self.group1 in self.user.groups.all()
        assert self.group2 in self.user.groups.all()

    def test_save_model_obj_removes_existing_groups(self) -> None:
        self.user.groups.add(self.group1)

        form = UserGroupForm(data={'groups': [self.group2.pk]}, instance=self.user)
        form.save_model_obj(self.request)

        self.user.refresh_from_db()
        assert self.group1 not in self.user.groups.all()
        assert self.group2 in self.user.groups.all()

    def test_save_model_obj_redirects_to_user_detail(self) -> None:
        form = UserGroupForm(data={'groups': [self.group1.pk]}, instance=self.user)
        response = form.save_model_obj(self.request)

        assert str(self.user.pk) in response.result['redirect']['url']

    def test_save_model_obj_invalid_group_returns_error(self) -> None:
        form = UserGroupForm(data={'groups': [99999]}, instance=self.user)
        response = form.save_model_obj(self.request)

        assert response.result is None
        assert self.user.groups.count() == 0
