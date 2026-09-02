from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import IntegrityError
from django.db.models import Subquery

from django_spire.conf import settings
from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.contrib.constructor.service.exceptions import ServiceError
from django_spire.metric.domain.statistic.services.factory_service import (
    StatisticFactoryService,
    StatisticGroupFactoryService,
    StatisticValueFactoryService,
)
from django_spire.metric.domain.statistic.services.intelligence_service import (
    StatisticGroupIntelligenceService,
    StatisticIntelligenceService,
    StatisticValueIntelligenceService,
)
from django_spire.metric.domain.statistic.services.processor_service import (
    StatisticGroupProcessorService,
    StatisticProcessorService,
    StatisticValueProcessorService,
)
from django_spire.metric.domain.statistic.services.tracking_service import StatisticTrackingService
from django_spire.metric.domain.statistic.services.transformation_service import (
    StatisticGroupTransformationService,
    StatisticTransformationService,
    StatisticValueTransformationService,
)

if TYPE_CHECKING:
    from django_spire.metric.domain.statistic.models import (
        Statistic,
        StatisticGroup,
        StatisticValue,
    )

logger = logging.getLogger(__name__)


class StatisticService(BaseDjangoModelService['Statistic']):
    obj: Statistic

    intelligence = StatisticIntelligenceService()
    processor = StatisticProcessorService()
    factory = StatisticFactoryService()
    tracking = StatisticTrackingService()
    transformation = StatisticTransformationService()

    @classmethod
    def record(
        cls,
        statistic_key: str,
        sub_domain_key: str,
        reference: str,
        value: float | str | Decimal = 1,
    ) -> StatisticValue:
        from django_spire.metric.domain.models import SubDomain  # noqa: PLC0415
        from django_spire.metric.domain.statistic.models import (  # noqa: PLC0415
            Statistic,
            StatisticValue,
        )

        reference_max_length = StatisticValue._meta.get_field('reference').max_length
        if len(reference) > reference_max_length:
            message = (
                f"Reference '{reference}' exceeds the maximum length "
                f'of {reference_max_length} characters'
            )
            raise ServiceError(message)

        statistic = Statistic.objects.for_key(statistic_key).active().not_deleted()
        statistic_ids = Subquery(statistic.values('pk')[:1])
        sub_domain_ids = Subquery(
            SubDomain.objects.for_key(sub_domain_key)
            .filter(domain_id__in=Subquery(statistic.values('group__domain_id')[:1]))
            .active()
            .not_deleted()
            .values('pk')[:1]
        )

        value_precision = StatisticValue._meta.get_field('value').decimal_places

        try:
            statistic_value = StatisticValue.objects.create(
                statistic_id=statistic_ids,
                sub_domain_id=sub_domain_ids,
                reference=reference,
                value=Decimal(value).quantize(Decimal(1).scaleb(-value_precision)),
            )
        except IntegrityError as error:
            message = f"Statistic '{statistic_key}' or sub-domain '{sub_domain_key}' not found"
            raise ServiceError(message) from error

        statistic_value.refresh_from_db()
        return statistic_value

    @classmethod
    def remote_record(
        cls,
        statistic_key: str,
        sub_domain_key: str,
        reference: str,
        value: float | str | Decimal = 1,
    ) -> dict | None:
        base_url = settings.DJANGO_SPIRE_REMOTE_API_URL
        key = settings.DJANGO_SPIRE_REMOTE_API_KEY

        if not base_url or not key:
            logger.warning(
                'Remote metric record skipped: DJANGO_SPIRE_REMOTE_API_URL or '
                'DJANGO_SPIRE_REMOTE_API_KEY is not configured'
            )
            return None

        from django_spire.metric.domain.statistic.services.rest_connector import (  # noqa: PLC0415
            SpireMetricRestConnector,
        )

        payload = {
            'reference': reference,
            'sub_domain_key': sub_domain_key,
            'value': str(Decimal(value)),
        }

        try:
            connector = SpireMetricRestConnector(base_url=base_url, api_key=key)
            return connector.record(statistic_key, payload)
        except Exception:
            logger.exception('Remote metric record failed')
            return None


class StatisticGroupService(BaseDjangoModelService['StatisticGroup']):
    obj: StatisticGroup

    intelligence = StatisticGroupIntelligenceService()
    processor = StatisticGroupProcessorService()
    factory = StatisticGroupFactoryService()
    transformation = StatisticGroupTransformationService()


class StatisticValueService(BaseDjangoModelService['StatisticValue']):
    obj: StatisticValue

    intelligence = StatisticValueIntelligenceService()
    processor = StatisticValueProcessorService()
    factory = StatisticValueFactoryService()
    transformation = StatisticValueTransformationService()
