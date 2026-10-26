from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.test import SimpleTestCase, override_settings

from django_spire.exceptions import DjangoSpireInvalidClassStringError
from django_spire.metric.metric import Metric, Target
from django_spire.metric.utils import discover_metric_registries

if TYPE_CHECKING:
    from django_spire.metric.specs import DomainSpec


def _store_domain() -> DomainSpec:
    return Metric.Domain(
        'store',
        name='Store',
        sub_domain_name='Channels',
        subdomains=[Metric.SubDomain('web', name='Web'), Metric.SubDomain('retail', name='Retail')],
        statistic_groups=[
            Metric.StatisticGroup(
                'orders',
                name='Orders',
                statistics=[
                    Metric.Statistic('created', name='Orders created'),
                    Metric.Statistic('revenue', name='Order revenue', value_type='currency'),
                ],
            )
        ],
    )


def _registry(domains: list | None = None, **attrs: Any) -> type[Metric]:
    defaults: dict[str, Any] = {'domains': domains if domains is not None else [_store_domain()]}
    defaults.update(attrs)
    return type('TestMetric', (Metric,), defaults)


class TargetEnumTestCase(SimpleTestCase):
    def test_target_is_exposed_on_metric(self):
        assert Metric.Target is Target
        assert Metric.Target.LOCAL == 'local'
        assert Metric.Target.REMOTE == 'remote'


class SpecConstructorTestCase(SimpleTestCase):
    def test_constructors_return_frozen_specs(self):
        domain = _store_domain()

        assert domain.key == 'store'
        assert len(domain.subdomains) == 2
        assert len(domain.statistic_groups) == 1
        assert domain.statistic_groups[0].statistics[1].value_type == 'currency'

        with pytest.raises(AttributeError):
            domain.name = 'Other'

    def test_stored_keys_are_namespaced(self):
        registry = _registry(domains=[_store_domain()])
        keys = registry.stored_keys()

        assert keys['domains'] == {'store'}
        assert keys['subdomains'] == {'store--web', 'store--retail'}
        assert keys['statistic_groups'] == {'store--orders'}
        assert keys['statistics'] == {'store--orders--created', 'store--orders--revenue'}


class SpecValidationTestCase(SimpleTestCase):
    def test_target_must_be_an_enum(self):
        with pytest.raises(TypeError, match=r'target must be a Metric.Target'):
            _registry(target='local')

    def test_remote_target_requires_remote_target_name(self):
        with pytest.raises(ValueError, match='remote_target must be a non-empty string'):
            _registry(target=Metric.Target.REMOTE)

    def test_remote_target_with_name_is_valid(self):
        registry = _registry(target=Metric.Target.REMOTE, remote_target='central')
        assert registry.target is Metric.Target.REMOTE

    def test_default_target_is_local(self):
        assert _registry().target is Metric.Target.LOCAL

    def test_domains_must_be_non_empty(self):
        with pytest.raises(ValueError, match='domains must be a non-empty list'):
            _registry(domains=[])

    def test_domain_entries_must_be_specs(self):
        with pytest.raises(TypeError):
            _registry(domains=['not-a-spec'])

    def test_duplicate_domain_keys(self):
        with pytest.raises(ValueError, match='declares duplicate domain key'):
            _registry(
                domains=[
                    Metric.Domain('store', name='Store'),
                    Metric.Domain('store', name='Store Again'),
                ]
            )

    def test_duplicate_sub_domain_keys_within_domain(self):
        with pytest.raises(ValueError, match='declares duplicate sub-domain key'):
            _registry(
                domains=[
                    Metric.Domain(
                        'store',
                        name='Store',
                        subdomains=[
                            Metric.SubDomain('web', name='Web'),
                            Metric.SubDomain('web', name='Web Again'),
                        ],
                    )
                ]
            )

    def test_sub_domain_keys_may_repeat_across_domains(self):
        registry = _registry(
            domains=[
                Metric.Domain(
                    'store', name='Store', subdomains=[Metric.SubDomain('web', name='Web')]
                ),
                Metric.Domain(
                    'shop', name='Shop', subdomains=[Metric.SubDomain('web', name='Web')]
                ),
            ]
        )
        assert registry.stored_keys()['subdomains'] == {'store--web', 'shop--web'}

    def test_duplicate_group_keys_within_domain(self):
        with pytest.raises(ValueError, match='declares duplicate statistic group key'):
            _registry(
                domains=[
                    Metric.Domain(
                        'store',
                        name='Store',
                        statistic_groups=[
                            Metric.StatisticGroup('orders', name='Orders'),
                            Metric.StatisticGroup('orders', name='Orders Again'),
                        ],
                    )
                ]
            )

    def test_duplicate_statistic_keys_within_group(self):
        with pytest.raises(ValueError, match='declares duplicate statistic key'):
            _registry(
                domains=[
                    Metric.Domain(
                        'store',
                        name='Store',
                        statistic_groups=[
                            Metric.StatisticGroup(
                                'orders',
                                name='Orders',
                                statistics=[
                                    Metric.Statistic('created', name='Created'),
                                    Metric.Statistic('created', name='Created Again'),
                                ],
                            )
                        ],
                    )
                ]
            )

    def test_key_must_be_slug_like(self):
        with pytest.raises(ValueError, match='must be lowercase letters'):
            _registry(domains=[Metric.Domain('Store', name='Store')])

    def test_key_must_not_contain_underscore(self):
        with pytest.raises(ValueError, match='must be lowercase letters'):
            _registry(domains=[Metric.Domain('my_key', name='Store')])

    def test_key_must_not_contain_double_hyphen(self):
        with pytest.raises(ValueError, match='must not contain'):
            _registry(domains=[Metric.Domain('sto--re', name='Store')])

    def test_key_length_is_capped(self):
        with pytest.raises(ValueError, match='exceeds 64 characters'):
            _registry(domains=[Metric.Domain('k' * 65, name='Store')])

    def test_stored_key_length_is_capped(self):
        with pytest.raises(ValueError, match='exceeds 64 characters'):
            _registry(
                domains=[
                    Metric.Domain(
                        'd' * 22,
                        name='Store',
                        statistic_groups=[
                            Metric.StatisticGroup(
                                'g' * 20,
                                name='Group',
                                statistics=[Metric.Statistic('s' * 20, name='Statistic')],
                            )
                        ],
                    )
                ]
            )

    def test_unknown_interval_rejected(self):
        with pytest.raises(ValueError, match='has unknown interval'):
            _registry(
                domains=[
                    Metric.Domain(
                        'store',
                        name='Store',
                        statistic_groups=[
                            Metric.StatisticGroup(
                                'orders',
                                name='Orders',
                                statistics=[
                                    Metric.Statistic('created', name='Created', interval='yearly')
                                ],
                            )
                        ],
                    )
                ]
            )

    def test_unknown_value_type_rejected(self):
        with pytest.raises(ValueError, match='has unknown value_type'):
            _registry(
                domains=[
                    Metric.Domain(
                        'store',
                        name='Store',
                        statistic_groups=[
                            Metric.StatisticGroup(
                                'orders',
                                name='Orders',
                                statistics=[
                                    Metric.Statistic('created', name='Created', value_type='text')
                                ],
                            )
                        ],
                    )
                ]
            )


class StatisticResolutionTestCase(SimpleTestCase):
    def setUp(self) -> None:
        self.registry = _registry(domains=[_store_domain()])

    def test_resolve_statistic(self):
        domain, statistic_group, statistic = self.registry._resolve_statistic(
            'store', 'orders', 'created'
        )
        assert domain.key == 'store'
        assert statistic_group.key == 'orders'
        assert statistic.key == 'created'

    def test_resolve_statistic_rejects_unknown(self):
        with pytest.raises(ValueError, match='No statistic declared for domain'):
            self.registry._resolve_statistic('store', 'orders', 'missing')
        with pytest.raises(ValueError, match='No statistic declared for domain'):
            self.registry._resolve_statistic('missing', 'orders', 'created')

    def test_resolve_sub_domain(self):
        domain = self.registry.domains[0]
        assert self.registry._resolve_sub_domain(domain, 'web').name == 'Web'
        with pytest.raises(ValueError, match='No sub-domain'):
            self.registry._resolve_sub_domain(domain, 'missing')


class DiscoverMetricRegistriesTestCase(SimpleTestCase):
    def test_empty_setting_returns_no_registries(self):
        with override_settings(DJANGO_SPIRE_METRIC_REGISTRY=[]):
            assert discover_metric_registries() == []

    def test_resolves_subclasses(self):
        with override_settings(
            DJANGO_SPIRE_METRIC_REGISTRY=['test_project.app.metrics.metrics.StoreMetric']
        ):
            registries = discover_metric_registries()

        assert len(registries) == 1
        assert registries[0].__name__ == 'StoreMetric'

    def test_rejects_non_metric_class(self):
        with (
            override_settings(
                DJANGO_SPIRE_METRIC_REGISTRY=['django_spire.exceptions.DjangoSpireError']
            ),
            pytest.raises(DjangoSpireInvalidClassStringError),
        ):
            discover_metric_registries()
