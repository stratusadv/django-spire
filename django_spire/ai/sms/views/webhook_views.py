from __future__ import annotations

import logging

from typing import TYPE_CHECKING

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse

from django_spire.ai.sms.decorators import twilio_auth_required
from django_spire.ai.sms.intelligence.workflows.sms_conversation_workflow import (
    sms_conversation_workflow,
)
from django_spire.ai.sms.models import (
    CODE_DIGIT_COUNT,
    SmsCodePurposeChoices,
    SmsConversation,
    SmsMessage,
    SmsPhoneNumber,
)
from django_spire.ai.sms.throttling import throttle_allowed
from django_spire.conf import settings

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


log = logging.getLogger(__name__)

PHONE_NUMBER_LENGTH_MIN = 11

REPLY_BODY_OVERSIZED = 'Your message is too long. Please send a shorter message.'
REPLY_SESSION_LOCKED = (
    'This session is locked. Generate an unlock code in the app, then text it here.'
)
REPLY_SESSION_UNLOCKED = 'Session unlocked. You can ask your questions now.'


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

    phone_number = SmsPhoneNumber.objects.verified_by_phone_number(from_number).first()

    if phone_number is None:
        log.warning('SMS received from unregistered number %s', from_number)
        return _twiml_response(None)

    if len(body) > settings.DJANGO_SPIRE_AI_SMS_BODY_LENGTH_MAX:
        return _twiml_response(REPLY_BODY_OVERSIZED)

    if phone_number.session_is_active:
        phone_number.session_touch()
        return _conversation_response(request, phone_number, body, message_sid)

    body_stripped = body.strip()

    if len(body_stripped) == CODE_DIGIT_COUNT and body_stripped.isdigit():
        code_valid = phone_number.code_confirm(
            body_stripped,
            SmsCodePurposeChoices.SESSION,
        )

        if code_valid:
            phone_number.session_open()
            return _twiml_response(REPLY_SESSION_UNLOCKED)

    return _twiml_response(REPLY_SESSION_LOCKED)


def _conversation_response(
    request: WSGIRequest,
    phone_number: SmsPhoneNumber,
    body: str,
    message_sid: str,
) -> HttpResponse:
    conversation_defaults = {'user': phone_number.user}

    conversation, _ = SmsConversation.objects.get_or_create(
        phone_number=phone_number.phone_number,
        defaults=conversation_defaults,
    )

    if conversation.user is None:
        conversation.user = phone_number.user
        conversation.save()

    message = conversation.add_message(body=body, is_inbound=True, twilio_sid=message_sid)

    request.user = phone_number.user

    sms_intel = sms_conversation_workflow(
        request=request,
        user_input=body,
        message_history=conversation.generate_message_history(),
        actor=phone_number.phone_number,
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
