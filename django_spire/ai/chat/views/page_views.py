from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.generic_views import portal_views

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@AppAuthController('ai_chat').permission_required('can_delete')
def home_view(request: WSGIRequest) -> TemplateResponse:
    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb(name='AI Chat')

    return portal_views.template_view(
        request,
        context_data={},
        page_title='AI Chat',
        page_description='Chat with AI',
        breadcrumbs=breadcrumbs,
        template='django_spire/ai/chat/page/home_page.html',
    )
