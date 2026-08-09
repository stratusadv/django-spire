from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.signage.models import Signage, SignagePresentation


class SignageFactoryService(BaseDjangoModelService['Signage']):
    obj: Signage


class SignagePresentationFactoryService(BaseDjangoModelService['SignagePresentation']):
    obj: SignagePresentation
