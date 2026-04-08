from __future__ import annotations

from typing import TYPE_CHECKING

from requests import Request

from django_spire.contrib.rest.service import BaseRestService
from test_project.apps.rest.services.rest.schema import PirateSchema

if TYPE_CHECKING:
    from test_project.apps.rest.models import Pirate


class PirateRestService(BaseRestService['Pirate', PirateSchema]):
    """REST service for syncing Pirates with external API."""
    obj: Pirate

    field_mapping = {
        'first_name': 'firstName',
        'last_name': 'lastName',
    }

    def update(self, obj: Pirate, request: Request, **kwargs) -> Pirate:
        qs = PirateSchema.objects.all()
