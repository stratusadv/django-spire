from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.presentation.models import Presentation


class PresentationIntelligenceService(BaseDjangoModelService['Presentation']):
    obj: Presentation
