from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class AuthGroupModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')

    def test_str_representation(self) -> None:
        assert str(self.group) == 'Test Group'

    def test_str_representation_with_special_characters(self) -> None:
        group = AuthGroup.objects.create(name='Test & Group <Special>')
        assert str(group) == 'Test & Group <Special>'

    def test_base_breadcrumb_returns_breadcrumbs(self) -> None:
        crumbs = AuthGroup.base_breadcrumb()
        assert crumbs is not None

    def test_breadcrumbs_with_pk_returns_breadcrumbs(self) -> None:
        crumbs = self.group.breadcrumbs()
        assert crumbs is not None

    def test_breadcrumbs_without_pk_returns_breadcrumbs(self) -> None:
        unsaved_group = AuthGroup(name='Unsaved Group')
        crumbs = unsaved_group.breadcrumbs()
        assert crumbs is not None

    def test_meta_proxy(self) -> None:
        assert AuthGroup._meta.proxy is True

    def test_meta_verbose_name(self) -> None:
        assert AuthGroup._meta.verbose_name == 'Auth Group'
        assert AuthGroup._meta.verbose_name_plural == 'Auth Groups'

    def test_group_creation(self) -> None:
        group = AuthGroup.objects.create(name='New Test Group')
        assert group.pk is not None
        assert group.name == 'New Test Group'

    def test_group_update(self) -> None:
        self.group.name = 'Updated Group Name'
        self.group.save()
        self.group.refresh_from_db()
        assert self.group.name == 'Updated Group Name'

    def test_group_deletion(self) -> None:
        group_pk = self.group.pk
        self.group.delete()
        assert AuthGroup.objects.filter(pk=group_pk).exists() is False

    def test_group_user_relationship(self) -> None:
        user = create_user(username='groupuser')
        self.group.user_set.add(user)
        assert user in self.group.user_set.all()
        assert self.group in user.groups.all()

    def test_group_permissions_relationship(self) -> None:
        assert hasattr(self.group, 'permissions')

    def test_group_name_max_length(self) -> None:
        max_length = AuthGroup._meta.get_field('name').max_length
        assert max_length == 150

    def test_multiple_groups_creation(self) -> None:
        groups = [
            AuthGroup.objects.create(name=f'Group {i}')
            for i in range(5)
        ]
        assert len(groups) == 5
        assert AuthGroup.objects.count() >= 5

    def test_group_queryset_ordering(self) -> None:
        AuthGroup.objects.create(name='Zebra Group')
        AuthGroup.objects.create(name='Alpha Group')
        groups = AuthGroup.objects.all().order_by('name')
        names = list(groups.values_list('name', flat=True))
        assert names == sorted(names)
