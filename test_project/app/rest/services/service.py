from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

from test_project.app.rest.services.factory_service import PirateFactoryService

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from test_project.app.rest.models import Pirate


class PirateService(BaseDjangoModelService['Pirate']):
    obj: Pirate

    factory = PirateFactoryService()

    def save_model_obj(self, user: User | None = None, **field_data: dict) -> Pirate:
        obj, created = super().save_model_obj(**field_data)
        if user and created:
            obj.add_activity(
                user=user,
                verb='created',
                information=f'{user.get_full_name()} created pirate {obj}.',
            )
        return obj
