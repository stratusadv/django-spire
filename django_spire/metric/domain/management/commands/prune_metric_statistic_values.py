from __future__ import annotations

from django.core.management.base import BaseCommand

from django_spire.conf import settings
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService


class Command(BaseCommand):
    help = 'Prunes old metric statistic values and trims per-reference tracking caps.'

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        retention_days = getattr(settings, 'DJANGO_SPIRE_METRIC_RETENTION_DAYS', 90)

        if retention_days and retention_days > 0:
            pruned = StatisticTrackingService.prune_retention(retention_days=retention_days)
            self.stdout.write(
                f'Pruned {pruned} statistic value(s) older than {retention_days} day(s).'
            )
        else:
            self.stdout.write('Retention disabled: skipping age-based pruning.')

        trimmed = StatisticTrackingService.trim_all()
        self.stdout.write(f'Trimmed {trimmed} statistic value(s) beyond the tracking cap.')

        self.stdout.write(self.style.SUCCESS('Metric statistic values pruned successfully.'))
