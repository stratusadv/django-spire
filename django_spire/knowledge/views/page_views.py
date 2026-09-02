from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.sms.models import AuthSms
from django_spire.auth.sms.utils import phone_number_format_display
from django_spire.conf import settings
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.navigation import KnowledgeNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_knowledge.view_collection')
def home_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        context=KnowledgeNavigation().as_context() | {
            'collections': (
                Collection.objects
                .active()
                .parentless()
                .request_user_has_access(request)
            ),
            'sms_auth': AuthSms.objects.by_user(request.user).first(),
            'code_expiry_minutes': settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES,
            'sender_phone_number': phone_number_format_display(settings.TWILIO_PHONE_NUMBER),
        },
        template='django_spire/knowledge/page/home_page.html',
    )
