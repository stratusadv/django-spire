from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from django_spire.auth.sms.models import AuthSms
from django_spire.auth.sms.utils import phone_number_format_display
from django_spire.conf import settings

from test_project.app.auth_sms.navigation import AuthSmsNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def phone_verification_view(request: WSGIRequest) -> TemplateResponse:
    sms_auth = AuthSms.objects.by_user(request.user).first()

    nav = AuthSmsNavigation()
    nav.page_title = 'Phone Verification'
    nav.breadcrumbs.add('Phone Verification')

    context = nav.as_context()
    context['sms_auth'] = sms_auth
    context['code_expiry_minutes'] = settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES
    context['sender_phone_number'] = phone_number_format_display(settings.TWILIO_PHONE_NUMBER)

    return TemplateResponse(
        request,
        context=context,
        template='auth/sms/page/phone_verification_page.html'
    )
