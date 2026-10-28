from __future__ import annotations

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import Domain
from django_spire.metric.domain.statistic.models import Statistic, StatisticValue
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
)
from django_spire.metric.metric import Metric


class AlphaMetric(Metric):
    domains = [
        Metric.Domain(
            'alpha',
            name='Alpha',
            statistic_groups=[
                Metric.StatisticGroup('sales', name='Sales', statistics=[Metric.Statistic('count', name='Sales count')])
            ],
        )
    ]


class BetaMetric(Metric):
    domains = [
        Metric.Domain(
            'beta',
            name='Beta',
            statistic_groups=[
                Metric.StatisticGroup('stock', name='Stock', statistics=[Metric.Statistic('count', name='Stock count')])
            ],
        )
    ]


class RemoteGammaMetric(Metric):
    target = Metric.Target.REMOTE
    remote_target = 'central'
    domains = [
        Metric.Domain(
            'gamma',
            name='Gamma',
            statistic_groups=[
                Metric.StatisticGroup(
                    'shipments', name='Shipments', statistics=[Metric.Statistic('count', name='Shipments count')]
                )
            ],
        )
    ]


ALPHA_METRIC = 'django_spire.metric.domain.tests.test_management.AlphaMetric'
BETA_METRIC = 'django_spire.metric.domain.tests.test_management.BetaMetric'
GAMMA_METRIC = 'django_spire.metric.domain.tests.test_management.RemoteGammaMetric'


class PruneMetricStatisticValuesCommandTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_command_prunes_retention_and_trims_caps(self) -> None:
        self.statistic.services.processor.add_value(
            reference='old', sub_domain=self.sub_domain, value=1, value_timestamp=timezone.now() - timedelta(days=30)
        )
        for _ in range(5):
            self.statistic.services.tracking.track(self.sub_domain, reference='click')

        with override_settings(DJANGO_SPIRE_METRIC_RETENTION_DAYS=7):
            call_command('prune_metric_statistic_values')

        assert StatisticValue.objects.filter(reference='old').count() == 0
        assert StatisticValue.objects.filter(reference='click').count() == 5


class MetricBuildCommandTestCase(BaseTestCase):
    def test_check_on_empty_db_fails(self) -> None:
        out = StringIO()

        with pytest.raises(CommandError):
            call_command('metric_build', '--check', stdout=out)

        output = out.getvalue()
        assert 'missing: store' in output

    def test_build_then_check_succeeds(self) -> None:
        out = StringIO()
        call_command('metric_build', stdout=out)
        assert 'created 6' in out.getvalue()

        out = StringIO()
        call_command('metric_build', stdout=out)
        assert 'unchanged 6' in out.getvalue()

        call_command('metric_build', '--check', stdout=StringIO())

    def test_build_lists_orphans(self) -> None:
        create_test_domain(name='stray')
        out = StringIO()

        call_command('metric_build', stdout=out)

        assert 'orphan (not in any registry): domain stray' in out.getvalue()

    def test_invalid_registry_string_fails(self) -> None:
        with pytest.raises(CommandError):
            call_command('metric_build', '--registry', 'django_spire.exceptions.DjangoSpireError')

    def test_no_registries_configured(self) -> None:
        out = StringIO()
        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[]):
            call_command('metric_build', stdout=out)

        assert 'No metric registries configured' in out.getvalue()


class MetricBuildOrphanFlagTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain(name='stray')
        self.sub_domain = create_test_subdomain(domain=self.domain)
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_build_flags_orphaned_rows(self) -> None:
        call_command('metric_build', stdout=StringIO())

        for obj in (self.domain, self.sub_domain, self.group, self.statistic):
            obj.refresh_from_db()

        for obj in (self.domain, self.sub_domain, self.group, self.statistic):
            assert obj.is_orphaned is True

    def test_build_clears_flag_for_registered_rows(self) -> None:
        domain = Domain.objects.create(name='Store', key='store', sub_domain_name='Channels')
        domain.is_orphaned = True
        domain.save()

        call_command('metric_build', stdout=StringIO())

        domain.refresh_from_db()
        assert domain.is_orphaned is False

    def test_check_does_not_update_flag(self) -> None:
        call_command('metric_build', stdout=StringIO())
        self.domain.refresh_from_db()
        assert self.domain.is_orphaned is True

        stray_two = create_test_domain(name='stray_two')

        call_command('metric_build', '--check', stdout=StringIO())

        stray_two.refresh_from_db()
        self.domain.refresh_from_db()
        assert stray_two.is_orphaned is False
        assert self.domain.is_orphaned is True

    def test_build_ignores_soft_deleted_rows(self) -> None:
        self.domain.set_deleted()
        out = StringIO()

        call_command('metric_build', stdout=out)

        self.domain.refresh_from_db()
        assert self.domain.is_orphaned is False
        assert 'orphan (not in any registry): domain' not in out.getvalue()


class MetricBuildPartialAndRemoteTestCase(BaseTestCase):
    def test_partial_build_does_not_flag_other_registries(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[ALPHA_METRIC, BETA_METRIC]):
            call_command('metric_build', stdout=StringIO())
            out = StringIO()
            call_command('metric_build', '--registry', ALPHA_METRIC, stdout=out)

        output = out.getvalue()
        assert 'unchanged 3' in output
        assert 'orphan (not in any registry): domain beta' not in output
        assert Domain.objects.for_key('beta').get().is_orphaned is False
        assert Statistic.objects.for_key('beta--stock--count').get().is_orphaned is False

    def test_build_skips_remote_registries(self) -> None:
        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[ALPHA_METRIC, GAMMA_METRIC]):
            out = StringIO()
            call_command('metric_build', stdout=out)

        output = out.getvalue()
        assert 'skipped: targets a remote installation' in output
        assert Domain.objects.for_key('alpha').exists()
        assert not Domain.objects.for_key('gamma').exists()

    def test_remote_keys_do_not_count_as_declared(self) -> None:
        gamma = create_test_domain(name='gamma')

        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[ALPHA_METRIC, GAMMA_METRIC]):
            out = StringIO()
            call_command('metric_build', stdout=out)

        assert 'orphan (not in any registry): domain gamma' in out.getvalue()
        gamma.refresh_from_db()
        assert gamma.is_orphaned is True

    def test_build_with_only_remote_registries_flags_nothing(self) -> None:
        stray = create_test_domain(name='stray')

        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[GAMMA_METRIC]):
            out = StringIO()
            call_command('metric_build', stdout=out)

        output = out.getvalue()
        assert 'skipped: targets a remote installation' in output
        assert 'orphan' not in output
        stray.refresh_from_db()
        assert stray.is_orphaned is False
