from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.management.base import BaseCommand, CommandError

from django_spire.contrib.utils import get_object_from_module_string
from django_spire.metric import Metric, discover_metric_registries
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = 'Builds or checks the declarative metric structure from the registered Metric registries.'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only verify that the declared structure exists; exit non-zero when it does not.',
        )
        parser.add_argument(
            '--registry',
            type=str,
            default=None,
            help='Dotted path to a single Metric subclass instead of DJANGO_SPIRE_METRIC_REGISTRY.',
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        registries = self._get_registries(options['registry'])

        if not registries:
            self.stdout.write('No metric registries configured in DJANGO_SPIRE_METRIC_REGISTRY.')
            return

        failures = []

        for registry in registries:
            label = f'{registry.__module__}.{registry.__qualname__}'
            summary = registry.check() if options['check'] else registry.build()

            self.stdout.write(label)
            self.stdout.write(f'  created {summary.created}, updated {summary.updated}, unchanged {summary.unchanged}')

            for missing in summary.missing:
                self.stdout.write(self.style.WARNING(f'  missing: {missing}'))
            for error in summary.errors:
                self.stdout.write(self.style.ERROR(f'  error: {error}'))

            if not summary.ok:
                failures.append(label)

        if not options['check']:
            self._apply_orphans(registries)

        if failures:
            mode = 'check' if options['check'] else 'build'
            message = f'Metric {mode} failed for: {", ".join(failures)}'
            raise CommandError(message)

        if options['check']:
            self.stdout.write(self.style.SUCCESS('Metric structure check passed.'))
        else:
            self.stdout.write(self.style.SUCCESS('Metric structure built.'))

    def _get_registries(self, registry_string: str | None) -> list[type[Metric]]:
        if registry_string is not None:
            registry_class = get_object_from_module_string(registry_string)
            if not isinstance(registry_class, type) or not issubclass(registry_class, Metric):
                message = f'{registry_string} must be a subclass of Metric'
                raise CommandError(message)
            return [registry_class]

        return discover_metric_registries()

    def _apply_orphans(self, registries: list[type[Metric]]) -> None:
        declared: dict[str, set[str]] = {
            'domains': set(),
            'subdomains': set(),
            'statistic_groups': set(),
            'statistics': set(),
        }

        for registry in registries:
            for level, keys in registry.stored_keys().items():
                declared[level] |= keys

        flagged_total = 0
        cleared_total = 0

        for label, model_class, level in (
            ('domain', Domain, 'domains'),
            ('sub-domain', SubDomain, 'subdomains'),
            ('statistic group', StatisticGroup, 'statistic_groups'),
            ('statistic', Statistic, 'statistics'),
        ):
            keys = declared[level]
            to_flag: list[int] = []
            to_clear: list[int] = []

            for instance in model_class.objects.active().not_deleted():
                if instance.key in keys:
                    if instance.is_orphaned:
                        to_clear.append(instance.pk)
                else:
                    self.stdout.write(self.style.WARNING(f'  orphan (not in any registry): {label} {instance.key}'))
                    if not instance.is_orphaned:
                        to_flag.append(instance.pk)

            if to_flag:
                model_class.objects.filter(pk__in=to_flag).update(is_orphaned=True)
                flagged_total += len(to_flag)
            if to_clear:
                model_class.objects.filter(pk__in=to_clear).update(is_orphaned=False)
                cleared_total += len(to_clear)

        self.stdout.write(f'  orphan flag: flagged {flagged_total}, cleared {cleared_total}')
