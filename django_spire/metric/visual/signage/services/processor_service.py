from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.metric.visual.signage.models import Signage


class SignageProcessorService(BaseDjangoModelService['Signage']):
    obj: Signage
