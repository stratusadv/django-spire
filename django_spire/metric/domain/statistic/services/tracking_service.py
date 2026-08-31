from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import connection, transaction
from django.db.models import Count, QuerySet
from django.utils import timezone

from django_spire.conf import settings
from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from uuid import UUID

    from django_spire.metric.domain.statistic.models import Statistic, StatisticValue

    from django_spire.metric.domain.models import SubDomain

logger = logging.getLogger(__name__)

WRITE_TIMEOUT_MS = 2000

DELETE_BATCH_SIZE = 5000


class StatisticTrackingService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    def track(
        self, sub_domain: SubDomain, *, reference: str = 'page_click'
    ) -> StatisticValue | None:
        if sub_domain.domain_id != self.obj.group.domain_id:
            logger.warning(
                'Sub-domain %s does not belong to domain %s', sub_domain, self.obj.group.domain
            )
            return None

        try:
            self._apply_write_timeout()

            with transaction.atomic():
                return self.obj.services.processor.increment(
                    reference=reference, sub_domain=sub_domain
                )
        except Exception:
            logger.warning('Statistic tracking failed', exc_info=True)
            return None
        finally:
            self._reset_write_timeout()

    def trim(self, sub_domain: SubDomain, reference: str, *, max_values: int | None = None) -> int:
        cap = max_values or getattr(settings, 'DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX', 1000)

        values = self.obj.values.filter(sub_domain=sub_domain, reference=reference)
        retained_pks = list(values.order_by('-timestamp').values_list('pk', flat=True)[:cap])

        return self._delete_batch(values, retained_pks)

    @classmethod
    def track_many(cls, references: list[str]) -> None:
        from django_spire.metric.domain.models import SubDomain  # noqa: PLC0415
        from django_spire.metric.domain.statistic.models import (  # noqa: PLC0415
            Statistic,
            StatisticValue,
        )

        statistic_key = cls._parse_key(
            settings.DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY, 'statistic'
        )
        sub_domain_key = cls._parse_key(
            settings.DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY, 'sub domain'
        )

        if statistic_key is None or sub_domain_key is None:
            return

        statistic = (
            Statistic.objects.for_key(statistic_key)
            .active()
            .not_deleted()
            .select_related('group')
            .first()
        )
        sub_domain = SubDomain.objects.for_key(sub_domain_key).active().not_deleted().first()

        if statistic is None or sub_domain is None:
            logger.debug('Statistic tracking target not found')
            return

        if sub_domain.domain_id != statistic.group.domain_id:
            logger.warning(
                'Sub-domain %s does not belong to domain %s', sub_domain, statistic.group.domain
            )
            return

        rows = [
            StatisticValue(
                statistic=statistic, sub_domain=sub_domain, reference=reference, value=Decimal(1)
            )
            for reference in references
        ]

        with transaction.atomic():
            StatisticValue.objects.bulk_create(rows, batch_size=500)

    @classmethod
    def track_configured(cls, *, reference: str = 'page_click') -> StatisticValue | None:
        from django_spire.metric.domain.models import SubDomain  # noqa: PLC0415
        from django_spire.metric.domain.statistic.models import Statistic  # noqa: PLC0415

        statistic_key = cls._parse_key(
            settings.DJANGO_SPIRE_INTERNAL_METRIC_STATISTIC_KEY, 'statistic'
        )
        sub_domain_key = cls._parse_key(
            settings.DJANGO_SPIRE_INTERNAL_METRIC_SUB_DOMAIN_KEY, 'sub domain'
        )

        if statistic_key is None or sub_domain_key is None:
            return None

        statistic = Statistic.objects.for_key(statistic_key).active().not_deleted().first()
        sub_domain = SubDomain.objects.for_key(sub_domain_key).active().not_deleted().first()

        if statistic is None or sub_domain is None:
            logger.debug('Statistic tracking target not found')
            return None

        return statistic.services.tracking.track(sub_domain, reference=reference)

    @classmethod
    def prune_retention(cls, *, retention_days: int | None = None) -> int:
        from django_spire.metric.domain.statistic.models import StatisticValue  # noqa: PLC0415

        if retention_days is None:
            retention_days = getattr(settings, 'DJANGO_SPIRE_METRIC_RETENTION_DAYS', 90)

        if retention_days <= 0:
            return 0

        cutoff = timezone.now() - timedelta(days=retention_days)
        return cls._delete_batch(StatisticValue.objects.filter(timestamp__lt=cutoff), [])

    @classmethod
    def trim_all(cls, *, max_values: int | None = None) -> int:
        from django_spire.metric.domain.statistic.models import StatisticValue  # noqa: PLC0415

        cap = max_values or getattr(settings, 'DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX', 1000)

        groups = (
            StatisticValue.objects.values('statistic_id', 'sub_domain_id', 'reference')
            .annotate(count=Count('pk'))
            .filter(count__gt=cap)
        )

        total = 0
        for group in groups.iterator():
            values = StatisticValue.objects.filter(
                statistic_id=group['statistic_id'],
                sub_domain_id=group['sub_domain_id'],
                reference=group['reference'],
            )
            retained_pks = list(values.order_by('-timestamp').values_list('pk', flat=True)[:cap])
            total += cls._delete_batch(values, retained_pks)

        return total

    @staticmethod
    def _delete_batch(queryset: QuerySet[StatisticValue], retained_pks: list[int]) -> int:
        total = 0

        while True:
            expired_pks = list(
                queryset.exclude(pk__in=retained_pks).values_list('pk', flat=True)[
                    :DELETE_BATCH_SIZE
                ]
            )

            if not expired_pks:
                break

            deleted, _ = queryset.model.objects.filter(pk__in=expired_pks).delete()
            total += deleted

        return total

    @staticmethod
    def _parse_key(key: str, label: str) -> UUID | None:
        try:
            return uuid.UUID(str(key))
        except ValueError:
            logger.debug('Invalid %s key %r', label, key)
            return None

    @staticmethod
    def _apply_write_timeout() -> None:
        if connection.vendor != 'postgresql':
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute(f'SET statement_timeout = {WRITE_TIMEOUT_MS}')
        except Exception:
            logger.debug('Failed to apply statement timeout', exc_info=True)

    @staticmethod
    def _reset_write_timeout() -> None:
        if connection.vendor != 'postgresql':
            return

        try:
            with connection.cursor() as cursor:
                cursor.execute('SET statement_timeout = 0')
        except Exception:
            logger.debug('Failed to reset statement timeout', exc_info=True)
