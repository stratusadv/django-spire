from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.auth.group.navigation import AuthGroupNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('ai_chat').permission_required('can_delete')
def chat_view(request: WSGIRequest) -> TemplateResponse:
    nav = AuthGroupNavigation()
    nav.page_title = 'AI Chat'
    nav.page_description = 'Chat with AI'
    nav.breadcrumbs.add('AI Chat')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/ai/chat/page/chat_page.html', context=context)
