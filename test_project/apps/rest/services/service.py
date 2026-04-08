from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService
from test_project.apps.rest.services.rest.service import PirateRestService

if TYPE_CHECKING:
    from test_project.apps.rest.models import Pirate


class PirateService(BaseDjangoModelService['Pirate']):
    obj: Pirate
    rest = PirateRestService()
