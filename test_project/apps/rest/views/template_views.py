from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.generic_views import portal_views
from test_project.apps.rest.models import Pirate

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def list_items_view(request: WSGIRequest):
    pirates = Pirate.objects.all()

    pirate_rest_schemas = PirateRestSchema.objects.all()
    pirate_hat_schemas = PirateHatRestSchema.objects.all()
    pirate_sword_schemas = PirateSwordRestSchema.objects.all()

    Pirate.services.processor.update_hat_type()

    # Code in Service Above

    # pirate_rest_schemas = PirateRestSchema.objects.all()
    # pirate_hat_rest_schemas = pirate_rest_schemas.hats.all()
    #
    # for pirate in pirates:
    #     pirate.hat_type = pirate_hat_rest_schemas.get(id=pirate.pk).hat_type
    #     pirate.save()
    #
    #     pirate_rest_schema = pirate.to_rest_schema()
    #     pirate_rest_schema.save()


    return portal_views.infinite_scrolling_view(
        request,
        context_data={'pirates': pirates},
        queryset=pirates,
        queryset_name='pirates',
        template='rest/item/items.html'
    )
