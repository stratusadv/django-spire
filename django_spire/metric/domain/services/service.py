from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from django_spire.metric.domain.services.factory_service import (
    DomainFactoryService,
    SubDomainFactoryService,
)
from django_spire.metric.domain.services.intelligence_service import DomainIntelligenceService, \
    SubDomainIntelligenceService
from django_spire.metric.domain.services.processor_service import (
    DomainProcessorService,
    SubDomainProcessorService,
)
from django_spire.metric.domain.services.transformation_service import DomainTransformationService, \
    SubDomainTransformationService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_spire.metric.domain.models import Domain, SubDomain


class DomainService(BaseDjangoModelService['Domain']):
    obj: Domain

    intelligence = DomainIntelligenceService()
    processor = DomainProcessorService()
    factory = DomainFactoryService()
    transformation = DomainTransformationService()

    def save_model_obj(self, user: User, **field_data: dict) -> Domain:
        obj, created = super().save_model_obj(**field_data)
        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} task {obj.name}.'
        )

        return obj


class SubDomainService(BaseDjangoModelService['SubDomain']):
    obj: SubDomain

    intelligence = SubDomainIntelligenceService()
    processor = SubDomainProcessorService()
    factory = SubDomainFactoryService()
    transformation = SubDomainTransformationService()

    def save_model_obj(self, user: User, **field_data: dict) -> SubDomain:
        obj, created = super().save_model_obj(**field_data)
        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} task {obj.name}.'
        )

        return obj
