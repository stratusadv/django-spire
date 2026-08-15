from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from test_project.app.rest.services.factory_service import PirateFactoryService

if TYPE_CHECKING:
    from test_project.app.rest.models import Pirate


class PirateService(BaseDjangoModelService['Pirate']):
    obj: Pirate

    factory = PirateFactoryService()
