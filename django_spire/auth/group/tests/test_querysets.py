from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.group.querysets import GroupQuerySet
from django_spire.core.tests.test_cases import BaseTestCase


class GroupQuerySetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group_c = AuthGroup.objects.create(name='Charlie Group')
        self.group_a = AuthGroup.objects.create(name='Alpha Group')
        self.group_b = AuthGroup.objects.create(name='Beta Group')

    def test_active_returns_ordered_by_name(self) -> None:
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        names = list(result.values_list('name', flat=True))
        assert names == ['Alpha Group', 'Beta Group', 'Charlie Group']

    def test_active_returns_all_groups(self) -> None:
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() == 3

    def test_active_empty_queryset(self) -> None:
        AuthGroup.objects.all().delete()
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() == 0

    def test_active_single_group(self) -> None:
        AuthGroup.objects.all().delete()
        AuthGroup.objects.create(name='Single Group')
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() == 1

    def test_active_ordering_with_numbers(self) -> None:
        group1 = AuthGroup.objects.create(name='AAA First')
        group2 = AuthGroup.objects.create(name='BBB Second')
        group3 = AuthGroup.objects.create(name='CCC Third')
        queryset = AuthGroup.objects.filter(pk__in=[group1.pk, group2.pk, group3.pk])
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        names = list(result.values_list('name', flat=True))
        assert names == ['AAA First', 'BBB Second', 'CCC Third']

    def test_active_ordering_with_special_characters(self) -> None:
        AuthGroup.objects.create(name='!Special')
        AuthGroup.objects.create(name='@Another')
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() >= 2

    def test_active_ordering_case_sensitive(self) -> None:
        AuthGroup.objects.all().delete()
        AuthGroup.objects.create(name='alpha')
        AuthGroup.objects.create(name='Alpha')
        AuthGroup.objects.create(name='ALPHA')
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        names = list(result.values_list('name', flat=True))
        assert len(names) == 3

    def test_active_ordering_with_unicode(self) -> None:
        AuthGroup.objects.create(name='Ñame')
        AuthGroup.objects.create(name='Ääkkönen')
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() >= 2

    def test_active_is_chainable(self) -> None:
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active().filter(name__contains='Group')
        assert result.count() == 3

    def test_active_with_prefetch(self) -> None:
        queryset = AuthGroup.objects.all().prefetch_related('permissions')
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert result.count() == 3

    def test_active_returns_queryset(self) -> None:
        queryset = AuthGroup.objects.all()
        queryset.__class__ = GroupQuerySet
        result = queryset.active()
        assert hasattr(result, 'filter')
        assert hasattr(result, 'exclude')
