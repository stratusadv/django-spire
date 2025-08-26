from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from module.models import SpireChildApp


class SpireChildAppIntelligenceService(BaseDjangoModelService['SpireChildApp']):
    obj: SpireChildApp
