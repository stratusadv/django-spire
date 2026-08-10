from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from twilio.rest import Client

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.models import AuthSms
from django_spire.auth.sms.utils import phone_number_normalize
from django_spire.conf import settings
from django_spire.contrib.decorators import valid_ajax_request_required
from django_spire.contrib.responses.json_response import error_json_response, success_json_response


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def _request_field(request: WSGIRequest, key: str, default: str = '') -> str:
    value = request.POST.get(key)

    if value is not None:
        return value

    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return default

    value = body.get(key, default)

    return value if isinstance(value, str) else default


@login_required()
@valid_ajax_request_required
def enrollment_start_view(request: WSGIRequest) -> JsonResponse:
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_phone_number = settings.TWILIO_PHONE_NUMBER

    if not account_sid or not auth_token or not from_phone_number:
        return error_json_response(
            'Text message sending is not configured. Please try again later.'
        )

    phone_number_raw = _request_field(request, 'phone_number')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response('That phone number is not valid. Please check it and try again.')

    auth_sms = AuthSms.objects.filter(phone_number=phone_number_normalized).first()

    if auth_sms is not None and auth_sms.user_id != request.user.id:
        return error_json_response('That phone number is already in use by another account.')

    if auth_sms is None:
        auth_sms = AuthSms.objects.create(user=request.user, phone_number=phone_number_normalized)

    if not auth_sms.throttle_allowed():
        return error_json_response(
            'You have requested too many codes. Please wait a moment and try again.'
        )

    code = auth_sms.services.processor.issue_code(AuthSmsCodePurposeChoices.ENROLLMENT)
    expiry_minutes = settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES

    twilio_client = Client(account_sid, auth_token)

    twilio_client.messages.create(
        to=phone_number_normalized,
        from_=from_phone_number,
        body=f'Your verification code is {code}. It expires in {expiry_minutes} minutes.',
    )

    return success_json_response('Your verification code has been sent.')


@login_required()
@valid_ajax_request_required
def enrollment_confirm_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = _request_field(request, 'phone_number')
    code = _request_field(request, 'code')

    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response('That phone number is not valid. Please check it and try again.')

    phone_number = AuthSms.objects.filter(
        phone_number=phone_number_normalized, user=request.user
    ).first()

    if phone_number is None:
        return error_json_response(
            'We could not find a verification request for that phone number.'
        )

    code_valid = phone_number.services.processor.confirm_code(
        code, AuthSmsCodePurposeChoices.ENROLLMENT
    )

    if not code_valid:
        return error_json_response('That code is not valid or has expired. Please try again.')

    phone_number.services.processor.mark_verified()

    return success_json_response('Your phone number has been verified.')


@login_required()
@valid_ajax_request_required
def session_code_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = _request_field(request, 'phone_number')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response('That phone number is not valid. Please check it and try again.')

    phone_number = (
        AuthSms.objects.verified_by_phone_number(phone_number_normalized)
        .filter(user=request.user)
        .first()
    )

    if phone_number is None:
        return error_json_response('We could not find a verified phone number for your account.')

    return JsonResponse(
        {
            'code': phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION),
            'expiry_minutes': settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES,
        }
    )
