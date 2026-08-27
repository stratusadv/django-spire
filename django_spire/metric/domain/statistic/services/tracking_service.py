from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import connection, transaction

from django_spire.conf import settings
from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from uuid import UUID

    from django_spire.metric.domain.statistic.models import Statistic, StatisticValue

    from django_spire.metric.domain.models import SubDomain

logger = logging.getLogger(__name__)

WRITE_TIMEOUT_MS = 2000


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
