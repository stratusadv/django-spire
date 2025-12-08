from __future__ import annotations

from django_spire.auth.group.forms import GroupForm, GroupNamesForm, GroupUserForm
from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class GroupFormTestCase(BaseTestCase):
    def test_valid_form(self) -> None:
        form = GroupForm(data={'name': 'Test Group'})
        assert form.is_valid() is True

    def test_reserved_name_all_users(self) -> None:
        form = GroupForm(data={'name': 'All Users'})
        assert form.is_valid() is False
        assert 'name' in form.errors

    def test_reserved_name_all_users_case_insensitive(self) -> None:
        form = GroupForm(data={'name': 'all users'})
        assert form.is_valid() is False
        assert 'name' in form.errors

    def test_reserved_name_all_users_mixed_case(self) -> None:
        form = GroupForm(data={'name': 'ALL USERS'})
        assert form.is_valid() is False
        assert 'name' in form.errors

    def test_reserved_name_all_users_with_spaces(self) -> None:
        form = GroupForm(data={'name': 'All  Users'})
        assert form.is_valid() is True

    def test_empty_name(self) -> None:
        form = GroupForm(data={'name': ''})
        assert form.is_valid() is False

    def test_whitespace_only_name(self) -> None:
        form = GroupForm(data={'name': '   '})
        assert form.is_valid() is False

    def test_save_creates_group(self) -> None:
        form = GroupForm(data={'name': 'New Group'})
        assert form.is_valid() is True
        group = form.save()
        assert group.name == 'New Group'
        assert AuthGroup.objects.filter(name='New Group').exists() is True

    def test_save_updates_existing_group(self) -> None:
        group = AuthGroup.objects.create(name='Original Name')
        form = GroupForm(data={'name': 'Updated Name'}, instance=group)
        assert form.is_valid() is True
        updated_group = form.save()
        assert updated_group.pk == group.pk
        assert updated_group.name == 'Updated Name'

    def test_name_with_special_characters(self) -> None:
        form = GroupForm(data={'name': 'Test & Group <Special>'})
        assert form.is_valid() is True

    def test_name_with_unicode(self) -> None:
        form = GroupForm(data={'name': 'Tëst Grøup 日本語'})
        assert form.is_valid() is True

    def test_name_max_length(self) -> None:
        long_name = 'A' * 150
        form = GroupForm(data={'name': long_name})
        assert form.is_valid() is True

    def test_name_exceeds_max_length(self) -> None:
        long_name = 'A' * 151
        form = GroupForm(data={'name': long_name})
        assert form.is_valid() is False

    def test_duplicate_name_fails(self) -> None:
        AuthGroup.objects.create(name='Existing Group')
        form = GroupForm(data={'name': 'Existing Group'})
        assert form.is_valid() is False


class GroupNamesFormTestCase(BaseTestCase):
    def test_valid_json_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '["Group A", "Group B"]'})
        assert form.is_valid() is True
        assert form.cleaned_data['groups'] == ['Group A', 'Group B']

    def test_empty_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '[]'})
        assert form.is_valid() is True
        assert form.cleaned_data['groups'] == []

    def test_save_creates_groups(self) -> None:
        form = GroupNamesForm(data={'groups': '["Test A", "Test B"]'})
        assert form.is_valid() is True
        groups = form.save()
        assert len(groups) == 2

    def test_single_group(self) -> None:
        form = GroupNamesForm(data={'groups': '["Single Group"]'})
        assert form.is_valid() is True
        assert form.cleaned_data['groups'] == ['Single Group']

    def test_groups_with_special_characters(self) -> None:
        form = GroupNamesForm(data={'groups': '["Group & Co", "Test <Group>"]'})
        assert form.is_valid() is True
        assert len(form.cleaned_data['groups']) == 2

    def test_save_skips_existing_groups(self) -> None:
        AuthGroup.objects.create(name='Existing')
        form = GroupNamesForm(data={'groups': '["Existing", "New"]'})
        assert form.is_valid() is True
        groups = form.save()
        assert len(groups) == 1
        assert groups[0].name == 'New'

    def test_many_groups(self) -> None:
        group_names = [f'Group {i}' for i in range(20)]
        form = GroupNamesForm(data={'groups': str(group_names).replace("'", '"')})
        assert form.is_valid() is True
        assert len(form.cleaned_data['groups']) == 20


class GroupUserFormTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = create_user(username='user1', first_name='User', last_name='One')
        self.user2 = create_user(username='user2', first_name='User', last_name='Two')
        self.user3 = create_user(username='user3', first_name='User', last_name='Three')

    def test_valid_form_with_users(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, self.user2.pk]})
        assert form.is_valid() is True

    def test_valid_form_empty_users(self) -> None:
        form = GroupUserForm(data={'users': []})
        assert form.is_valid() is True

    def test_user_label(self) -> None:
        label = GroupUserForm.user_label(self.user1)
        assert label == 'User One'

    def test_single_user(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk]})
        assert form.is_valid() is True
        assert len(form.cleaned_data['users']) == 1

    def test_all_users(self) -> None:
        form = GroupUserForm(data={'users': [self.user1.pk, self.user2.pk, self.user3.pk]})
        assert form.is_valid() is True
        assert len(form.cleaned_data['users']) == 3

    def test_invalid_user_id(self) -> None:
        form = GroupUserForm(data={'users': [99999]})
        assert form.is_valid() is False

    def test_inactive_user_excluded_from_queryset(self) -> None:
        inactive_user = create_user(username='inactive', is_active=False)
        form = GroupUserForm()
        user_ids = list(form.fields['users'].queryset.values_list('id', flat=True))
        assert inactive_user.pk not in user_ids

    def test_user_label_with_empty_names(self) -> None:
        user = create_user(username='noname', first_name='', last_name='')
        label = GroupUserForm.user_label(user)
        assert label == ''
