from __future__ import annotations

from django_spire.auth.group.factories import bulk_create_groups_from_names
from django_spire.auth.group.models import AuthGroup
from django_spire.core.tests.test_cases import BaseTestCase


class BulkCreateGroupsFromNamesTestCase(BaseTestCase):
    def test_creates_new_groups(self) -> None:
        names = ['Group A', 'Group B', 'Group C']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3
        assert AuthGroup.objects.filter(name__in=names).count() == 3

    def test_skips_existing_groups(self) -> None:
        AuthGroup.objects.create(name='Existing Group')
        names = ['Existing Group', 'New Group']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 1
        assert groups[0].name == 'New Group'

    def test_empty_list(self) -> None:
        groups = bulk_create_groups_from_names([])
        assert len(groups) == 0

    def test_all_existing_groups(self) -> None:
        AuthGroup.objects.create(name='Group A')
        AuthGroup.objects.create(name='Group B')
        groups = bulk_create_groups_from_names(['Group A', 'Group B'])
        assert len(groups) == 0

    def test_single_group(self) -> None:
        groups = bulk_create_groups_from_names(['Single Group'])
        assert len(groups) == 1
        assert groups[0].name == 'Single Group'

    def test_unique_names_only(self) -> None:
        groups = bulk_create_groups_from_names(['Group A', 'Group B'])
        assert len(groups) == 2

    def test_groups_are_persisted(self) -> None:
        bulk_create_groups_from_names(['Persisted Group'])
        assert AuthGroup.objects.filter(name='Persisted Group').exists()

    def test_mixed_existing_and_new(self) -> None:
        AuthGroup.objects.create(name='Existing 1')
        AuthGroup.objects.create(name='Existing 2')
        names = ['Existing 1', 'New 1', 'Existing 2', 'New 2']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 2
        group_names = [g.name for g in groups]
        assert 'New 1' in group_names
        assert 'New 2' in group_names

    def test_special_characters_in_names(self) -> None:
        names = ['Group & Co', 'Test <Group>', 'Group "Name"']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_unicode_names(self) -> None:
        names = ['Tëst Grøup', '日本語グループ', 'Группа']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_whitespace_names(self) -> None:
        names = ['  Spaces  ', 'Tab\tGroup']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 2

    def test_many_groups(self) -> None:
        names = [f'Group {i}' for i in range(50)]
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 50

    def test_returns_group_instances(self) -> None:
        groups = bulk_create_groups_from_names(['Test Group'])
        assert isinstance(groups[0], AuthGroup)

    def test_groups_have_primary_keys(self) -> None:
        groups = bulk_create_groups_from_names(['PK Test Group'])
        for group in groups:
            assert group.pk is not None

    def test_duplicate_names_in_input_list(self) -> None:
        names = ['Duplicate', 'Duplicate', 'Duplicate']
        groups = bulk_create_groups_from_names(names)
        assert AuthGroup.objects.filter(name='Duplicate').count() >= 1

    def test_empty_string_name(self) -> None:
        names = ['', 'Valid Group']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) >= 1

    def test_very_long_name(self) -> None:
        long_name = 'A' * 150
        groups = bulk_create_groups_from_names([long_name])
        assert len(groups) == 1
        assert groups[0].name == long_name

    def test_name_with_only_whitespace(self) -> None:
        names = ['   ', '\t\t', '\n\n']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_name_with_leading_trailing_whitespace(self) -> None:
        names = ['  Leading', 'Trailing  ', '  Both  ']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_case_sensitive_names(self) -> None:
        names = ['group', 'Group', 'GROUP']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_numeric_names(self) -> None:
        names = ['123', '456', '789']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_mixed_alphanumeric_names(self) -> None:
        names = ['Group1', '2Group', 'Gr0up3']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 3

    def test_names_with_newlines(self) -> None:
        names = ['Group\nWith\nNewlines']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 1

    def test_names_with_null_characters(self) -> None:
        names = ['Group\x00Name']
        groups = bulk_create_groups_from_names(names)
        assert len(groups) == 1

    def test_preserves_order_of_creation(self) -> None:
        names = ['First', 'Second', 'Third']
        groups = bulk_create_groups_from_names(names)
        group_names = [g.name for g in groups]
        assert group_names == names

    def test_does_not_modify_existing_groups(self) -> None:
        existing = AuthGroup.objects.create(name='Existing')
        original_pk = existing.pk
        bulk_create_groups_from_names(['Existing', 'New'])
        existing.refresh_from_db()
        assert existing.pk == original_pk
