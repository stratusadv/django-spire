from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.generic_views import portal_views
from test_project.apps.rest.models import Pirate

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def list_items_view(request: WSGIRequest):
    pirates = Pirate.schema.objects.all()

    return portal_views.infinite_scrolling_view(
        request,
        context_data={'pirates': pirates},
        queryset=pirates,
        queryset_name='pirates',
        template='rest/item/items.html'
    )
