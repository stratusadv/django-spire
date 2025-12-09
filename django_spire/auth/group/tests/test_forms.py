from __future__ import annotations

from django_spire.auth.group.forms import GroupForm, GroupNamesForm, GroupUserForm
from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class GroupFormTestCase(BaseTestCase):
    def test_valid_form(self) -> None:
        form = GroupForm(data={'name': 'Test Group'})
        assert form.is_valid()

    def test_reserved_name_all_users(self) -> None:
        form = GroupForm(data={'name': 'All Users'})
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_reserved_name_all_users_case_insensitive(self) -> None:
        form = GroupForm(data={'name': 'all users'})
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_reserved_name_all_users_mixed_case(self) -> None:
        form = GroupForm(data={'name': 'ALL USERS'})
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_reserved_name_all_users_with_extra_spaces(self) -> None:
        form = GroupForm(data={'name': 'All  Users'})
        assert form.is_valid()

    def test_empty_name(self) -> None:
        form = GroupForm(data={'name': ''})
        assert not form.is_valid()

    def test_whitespace_only_name(self) -> None:
        form = GroupForm(data={'name': '   '})
        assert not form.is_valid()

    def test_save_creates_group(self) -> None:
        form = GroupForm(data={'name': 'New Group'})
        assert form.is_valid()
        group = form.save()
        assert group.name == 'New Group'
        assert AuthGroup.objects.filter(name='New Group').exists()

    def test_save_updates_existing_group(self) -> None:
        group = AuthGroup.objects.create(name='Original Name')
        form = GroupForm(data={'name': 'Updated Name'}, instance=group)
        assert form.is_valid()
        updated_group = form.save()
        assert updated_group.pk == group.pk
        assert updated_group.name == 'Updated Name'

    def test_name_with_special_characters(self) -> None:
        form = GroupForm(data={'name': 'Test & Group <Special>'})
        assert form.is_valid()

    def test_name_with_unicode(self) -> None:
        form = GroupForm(data={'name': 'Tëst Grøup 日本語'})
        assert form.is_valid()

    def test_name_max_length(self) -> None:
        long_name = 'A' * 150
        form = GroupForm(data={'name': long_name})
        assert form.is_valid()

    def test_name_exceeds_max_length(self) -> None:
        long_name = 'A' * 151
        form = GroupForm(data={'name': long_name})
        assert not form.is_valid()

    def test_duplicate_name_fails(self) -> None:
        AuthGroup.objects.create(name='Existing Group')
        form = GroupForm(data={'name': 'Existing Group'})
        assert not form.is_valid()

    def test_duplicate_name_case_sensitive(self) -> None:
        AuthGroup.objects.create(name='Existing Group')
        form = GroupForm(data={'name': 'existing group'})
        assert form.is_valid()

    def test_reserved_name_error_message(self) -> None:
        form = GroupForm(data={'name': 'All Users'})
        form.is_valid()
        assert 'reserved' in form.errors['name'][0].lower()

    def test_form_excludes_permissions_field(self) -> None:
        form = GroupForm()
        assert 'permissions' not in form.fields

    def test_update_to_reserved_name_fails(self) -> None:
        group = AuthGroup.objects.create(name='Original')
        form = GroupForm(data={'name': 'All Users'}, instance=group)
        assert not form.is_valid()

    def test_name_with_leading_trailing_whitespace(self) -> None:
        form = GroupForm(data={'name': '  Test Group  '})
        assert form.is_valid()

    def test_name_with_newline(self) -> None:
        form = GroupForm(data={'name': 'Test\nGroup'})
        assert form.is_valid()

    def test_name_with_tab(self) -> None:
        form = GroupForm(data={'name': 'Test\tGroup'})
        assert form.is_valid()

    def test_numeric_name(self) -> None:
        form = GroupForm(data={'name': '12345'})
        assert form.is_valid()


class GroupNamesFormTestCase(BaseTestCase):
    def test_valid_json_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '["Group A", "Group B"]'})
        assert form.is_valid()
        assert form.cleaned_data['groups'] == ['Group A', 'Group B']

    def test_empty_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '[]'})
        assert form.is_valid()
        assert form.cleaned_data['groups'] == []

    def test_save_creates_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '["Test A", "Test B"]'})
        assert form.is_valid()
        groups = form.save()
        assert len(groups) == 2

    def test_single_group(self) -> None:
        form = GroupNamesForm(data={'groups': '["Single Group"]'})
        assert form.is_valid()
        assert form.cleaned_data['groups'] == ['Single Group']

    def test_groups_with_special_characters(self) -> None:
        form = GroupNamesForm(data={'groups': '["Group & Co", "Test <Group>"]'})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 2

    def test_save_skips_existing_groups(self) -> None:
        AuthGroup.objects.create(name='Existing')
        form = GroupNamesForm(data={'groups': '["Existing", "New"]'})
        assert form.is_valid()
        groups = form.save()
        assert len(groups) == 1
        assert groups[0].name == 'New'

    def test_many_groups(self) -> None:
        group_names = [f'Group {i}' for i in range(20)]
        form = GroupNamesForm(data={'groups': str(group_names).replace("'", '"')})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 20

    def test_unicode_group_names(self) -> None:
        form = GroupNamesForm(data={'groups': '["Tëst", "日本語"]'})
        assert form.is_valid()
        assert len(form.cleaned_data['groups']) == 2

    def test_empty_string_in_list(self) -> None:
        form = GroupNamesForm(data={'groups': '["", "Valid"]'})
        assert form.is_valid()
        assert '' in form.cleaned_data['groups']

    def test_whitespace_group_names(self) -> None:
        form = GroupNamesForm(data={'groups': '["  Spaces  ", "Normal"]'})
        assert form.is_valid()

    def test_nested_json_fails(self) -> None:
        form = GroupNamesForm(data={'groups': '[["nested"]]'})
        assert form.is_valid()

    def test_null_in_list(self) -> None:
        form = GroupNamesForm(data={'groups': '[null, "Valid"]'})
        assert form.is_valid()

    def test_number_in_list(self) -> None:
        form = GroupNamesForm(data={'groups': '[123, "Valid"]'})
        assert form.is_valid()

    def test_duplicate_names_in_list(self) -> None:
        form = GroupNamesForm(data={'groups': '["Dup", "Dup", "Dup"]'})
        assert form.is_valid()

    def test_groups_field_not_required(self) -> None:
        form = GroupNamesForm(data={})
        assert not form.is_valid()


class GroupUserFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = create_user(username='user1', first_name='User', last_name='One')
        self.user2 = create_user(username='user2', first_name='User', last_name='Two')
        self.user3 = create_user(username='user3', first_name='User', last_name='Three')

    def test_valid_form_with_users(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, self.user2.pk]})
        assert form.is_valid()

    def test_valid_form_empty_users(self) -> None:
        form = GroupUserForm(data={'users': []})
        assert form.is_valid()

    def test_user_label(self) -> None:
        label = GroupUserForm.user_label(self.user1)
        assert label == 'User One'

    def test_single_user(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['users']) == 1

    def test_all_users(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, self.user2.pk, self.user3.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['users']) == 3

    def test_invalid_user_id(self) -> None:
        form = GroupUserForm(data={'users': [99999]})
        assert not form.is_valid()

    def test_inactive_user_excluded_from_queryset(self) -> None:
        inactive_user = create_user(username='inactive', is_active=False)
        form = GroupUserForm()
        user_ids = list(form.fields['users'].queryset.values_list('id', flat=True))
        assert inactive_user.pk not in user_ids

    def test_user_label_with_empty_names(self) -> None:
        user = create_user(username='noname', first_name='', last_name='')
        label = GroupUserForm.user_label(user)
        assert label == ''

    def test_user_label_first_name_only(self) -> None:
        user = create_user(username='firstonly', first_name='First', last_name='')
        label = GroupUserForm.user_label(user)
        assert 'First' in label

    def test_user_label_last_name_only(self) -> None:
        user = create_user(username='lastonly', first_name='', last_name='Last')
        label = GroupUserForm.user_label(user)
        assert 'Last' in label

    def test_mixed_valid_invalid_user_ids(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, 99999]})
        assert not form.is_valid()

    def test_duplicate_user_ids(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, self.user1.pk]})
        assert form.is_valid()
        assert len(form.cleaned_data['users']) == 1

    def test_negative_user_id(self) -> None:
        form = GroupUserForm(data={'users': [-1]})
        assert not form.is_valid()

    def test_string_user_id(self) -> None:
        form = GroupUserForm(data={'users': ['invalid']})
        assert not form.is_valid()

    def test_queryset_excludes_inactive_users(self) -> None:
        create_user(username='inactive1', is_active=False)
        create_user(username='inactive2', is_active=False)
        form = GroupUserForm()
        queryset = form.fields['users'].queryset
        assert not queryset.filter(is_active=False).exists()

    def test_form_users_field_not_required(self) -> None:
        form = GroupUserForm(data={})
        assert form.is_valid()

    def test_user_label_with_unicode(self) -> None:
        user = create_user(username='unicode', first_name='Tëst', last_name='Üsér')
        label = GroupUserForm.user_label(user)
        assert 'Tëst' in label
        assert 'Üsér' in label

    def test_zero_user_id(self) -> None:
        form = GroupUserForm(data={'users': [0]})
        assert not form.is_valid()
