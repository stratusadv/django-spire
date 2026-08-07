from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse

from django_spire.ai.sms.intelligence.workflow import sms_conversation_workflow
from django_spire.ai.sms.models import (
    SmsConversation,
    SmsMessage,
)
from django_spire.auth.sms.choices import SmsAuthCodePurposeChoices
from django_spire.auth.sms.constants import CODE_DIGIT_COUNT, PHONE_NUMBER_LENGTH_MIN
from django_spire.auth.sms.decorators import twilio_auth_required
from django_spire.auth.sms.models import SmsAuth
from django_spire.auth.sms.throttling import throttle_allowed
from django_spire.conf import settings

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


log = logging.getLogger(__name__)


@csrf_exempt
@require_POST
@twilio_auth_required
def webhook_view(request: WSGIRequest) -> HttpResponse:
    from_number = request.POST.get('From', '')
    body = request.POST.get('Body', '')
    message_sid = request.POST.get('MessageSid', '')

    if len(from_number) < PHONE_NUMBER_LENGTH_MIN:
        return HttpResponseForbidden()

    if message_sid and SmsMessage.objects.inbound_by_twilio_sid(message_sid).exists():
        log.info('Duplicate SMS webhook delivery ignored for sid %s', message_sid)
        return _twiml_response(None)

    if not throttle_allowed(from_number):
        log.warning('SMS throttle exceeded for %s', from_number)
        return _twiml_response(None)

    sms_auth = SmsAuth.objects.verified_by_phone_number(from_number).first()

    if sms_auth is None:
        log.warning('SMS received from unregistered number %s', from_number)
        return _twiml_response(None)

    if len(body) > settings.DJANGO_SPIRE_AI_SMS_BODY_LENGTH_MAX:
        return _twiml_response('Your message is too long. Please send a shorter message.')

    if sms_auth.services.session_is_active:
        sms_auth.services.session_touch()
        return _conversation_response(request, sms_auth, body, message_sid)

    body_stripped = body.strip()

    if len(body_stripped) == CODE_DIGIT_COUNT and body_stripped.isdigit():
        code_valid = sms_auth.services.code_confirm(
            body_stripped,
            SmsAuthCodePurposeChoices.SESSION,
        )

        if code_valid:
            sms_auth.services.session_open()
            return _twiml_response('Session unlocked. You can ask your questions now.')

    return _twiml_response(
        'This session is locked. Generate an unlock code in the app, then text it here.'
    )


def _conversation_response(
    request: WSGIRequest,
    sms_auth: SmsAuth,
    body: str,
    message_sid: str,
) -> HttpResponse:
    conversation_defaults = {'user': sms_auth.user}

    conversation, _ = SmsConversation.objects.get_or_create(
        phone_number=sms_auth.phone_number,
        defaults=conversation_defaults,
    )

    if conversation.user is None:
        conversation.user = sms_auth.user
        conversation.save()

    message = conversation.add_message(body=body, is_inbound=True, twilio_sid=message_sid)

    request.user = sms_auth.user

    sms_intel = sms_conversation_workflow(
        request=request,
        user_input=body,
        message_history=conversation.generate_message_history(),
        actor=sms_auth.phone_number,
    )

    conversation.add_message(
        body=sms_intel.body,
        is_inbound=False,
        twilio_sid=message_sid,
        is_processed=True,
    )

    message.is_processed = True
    message.save()

    return _twiml_response(sms_intel.body)


def _twiml_response(body: str | None) -> HttpResponse:
    twiml_response = MessagingResponse()

    if body is not None:
        twiml_response.message(body)

    return HttpResponse(twiml_response, content_type='text/xml')
