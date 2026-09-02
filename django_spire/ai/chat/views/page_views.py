from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.auth.group.navigation import AuthGroupNavigation
from django_spire.auth.permissions.decorators import permission_required

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_ai_chat.delete_chat')
def chat_view(request: WSGIRequest) -> TemplateResponse:
    nav = AuthGroupNavigation()
    nav.page_title = 'AI Chat'
    nav.page_description = 'Chat with AI'
    nav.breadcrumbs.add('AI Chat')
    context = nav.as_context()
    return TemplateResponse(request, 'django_spire/ai/chat/page/chat_page.html', context=context)
