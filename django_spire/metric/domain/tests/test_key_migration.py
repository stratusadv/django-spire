from __future__ import annotations

from importlib import import_module

from django.apps import apps
from django.test import TestCase

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup

MIGRATION_MODULE = 'django_spire.metric.domain.migrations.0012_metric_key_object_separator'


def _migration_functions() -> tuple:
    module = import_module(MIGRATION_MODULE)
    return module.forward, module.reverse


class KeySeparatorMigrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.domain = Domain.objects.create(key='store', name='Store', sub_domain_name='Channels')
        cls.sub_domain = SubDomain.objects.create(domain=cls.domain, key='store__web', name='Web')
        cls.group = StatisticGroup.objects.create(domain=cls.domain, key='store__orders', name='Orders')
        cls.statistic = Statistic.objects.create(group=cls.group, key='store__orders__created', name='Created')
        cls.taken = SubDomain.objects.create(domain=cls.domain, key='dup--target', name='Taken')
        cls.clashing = SubDomain.objects.create(domain=cls.domain, key='dup__target', name='Clashing')

    def test_forward_rewrites_object_separator(self):
        forward, _reverse = _migration_functions()
        forward(apps, None)
        self.domain.refresh_from_db()
        self.sub_domain.refresh_from_db()
        self.group.refresh_from_db()
        self.statistic.refresh_from_db()
        assert self.domain.key == 'store'
        assert self.sub_domain.key == 'store--web'
        assert self.group.key == 'store--orders'
        assert self.statistic.key == 'store--orders--created'

    def test_forward_skips_colliding_target(self):
        forward, _reverse = _migration_functions()
        forward(apps, None)
        self.clashing.refresh_from_db()
        assert self.clashing.key == 'dup__target'

    def test_forward_is_idempotent(self):
        forward, _reverse = _migration_functions()
        forward(apps, None)
        forward(apps, None)
        self.sub_domain.refresh_from_db()
        assert self.sub_domain.key == 'store--web'

    def test_reverse_restores_object_separator(self):
        forward, reverse = _migration_functions()
        forward(apps, None)
        reverse(apps, None)
        self.sub_domain.refresh_from_db()
        self.statistic.refresh_from_db()
        assert self.sub_domain.key == 'store__web'
        assert self.statistic.key == 'store__orders__created'
