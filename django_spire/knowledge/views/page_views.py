from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def home_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'collections': Collection.objects.active().parentless().request_user_has_access(request)
    }
    context_data['page_title'] = 'Collection'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'Knowledge', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='django_spire/knowledge/page/home_page.html'
    )
