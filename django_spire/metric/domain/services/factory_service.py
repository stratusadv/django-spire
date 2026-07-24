from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.domain.models import Domain, SubDomain


class DomainFactoryService(BaseDjangoModelService['Domain']):
    obj: Domain


class SubDomainFactoryService(BaseDjangoModelService['SubDomain']):
    obj: SubDomain
