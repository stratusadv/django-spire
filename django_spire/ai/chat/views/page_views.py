from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib import Breadcrumbs

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('ai_chat').permission_required('can_delete')
def chat_view(request: WSGIRequest) -> TemplateResponse:
    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_breadcrumb(name='AI Chat')

    context = {
        'page_title': 'AI Chat',
        'page_description': 'Chat with AI',
        'breadcrumbs': list(breadcrumbs),
    }

    return TemplateResponse(request, 'django_spire/ai/chat/page/chat_page.html', context=context)
