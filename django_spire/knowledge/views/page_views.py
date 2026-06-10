from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.navigation import CollectionNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def home_view(request: WSGIRequest) -> TemplateResponse:
    nav = CollectionNavigation()
    nav.page_title = 'Collection'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Knowledge')
    context = nav.as_context()
    context['collections'] = (
        Collection.objects.active().parentless().request_user_has_access(request)
    )
    return TemplateResponse(
        request, context=context, template='django_spire/knowledge/page/home_page.html'
    )
