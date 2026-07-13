from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.handlers.wsgi import WSGIRequest
from django_glue.access.access import GlueAccess
from django_glue import Glue

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from test_project.app.rest.models import Pirate


class PirateFactoryService(BaseDjangoModelService['Pirate']):
    obj: Pirate

    @Glue.Attribute(access=GlueAccess.CHANGE)
    def duplicate(self, request: WSGIRequest) -> dict:
        new_pirate = self.obj_class.services.save_model_obj(
            user=request.user,
            first_name=self.obj.first_name,
            last_name=self.obj.last_name,
            email=self.obj.email,
            username=f'{self.obj.username}_copy',
        )
        return {'success': True, 'new_pirate_id': new_pirate.id}
