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
