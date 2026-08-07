from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from twilio.rest import Client

from django_spire.auth.sms.choices import SmsAuthCodePurposeChoices
from django_spire.auth.sms.models import SmsAuth
from django_spire.auth.sms.throttling import throttle_allowed
from django_spire.auth.sms.utils import phone_number_normalize
from django_spire.conf import settings
from django_spire.contrib.decorators import valid_ajax_request_required
from django_spire.contrib.responses.json_response import (
    error_json_response,
    success_json_response,
)


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


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

    phone_number_raw = request.POST.get('phone_number', '')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response(
            'That phone number is not valid. Please check it and try again.'
        )

    if not throttle_allowed(phone_number_normalized):
        return error_json_response(
            'You have requested too many codes. Please wait a moment and try again.'
        )

    sms_auth = SmsAuth.objects.filter(phone_number=phone_number_normalized).first()

    if sms_auth is not None and sms_auth.user_id != request.user.id:
        return error_json_response(
            'That phone number is already in use by another account.'
        )

    if sms_auth is None:
        phone_number = SmsAuth.objects.create(
            user=request.user, phone_number=phone_number_normalized
        )
    else:
        phone_number = sms_auth

    code = phone_number.services.code_issue(SmsAuthCodePurposeChoices.ENROLLMENT)
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
    phone_number_raw = request.POST.get('phone_number', '')
    code = request.POST.get('code', '')

    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response(
            'That phone number is not valid. Please check it and try again.'
        )

    phone_number = SmsAuth.objects.filter(
        phone_number=phone_number_normalized, user=request.user
    ).first()

    if phone_number is None:
        return error_json_response(
            'We could not find a verification request for that phone number.'
        )

    code_valid = phone_number.services.code_confirm(code, SmsAuthCodePurposeChoices.ENROLLMENT)

    if not code_valid:
        return error_json_response(
            'That code is not valid or has expired. Please try again.'
        )

    phone_number.services.verified_mark()

    return success_json_response('Your phone number has been verified.')


@login_required()
@valid_ajax_request_required
def session_code_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = request.POST.get('phone_number', '')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return error_json_response('That phone number is not valid. Please check it and try again.')

    phone_number = (
        SmsAuth.objects.verified_by_phone_number(phone_number_normalized)
        .filter(user=request.user)
        .first()
    )

    if phone_number is None:
        return error_json_response('We could not find a verified phone number for your account.')

    return JsonResponse(
        {
            'code': phone_number.services.code_issue(SmsAuthCodePurposeChoices.SESSION),
            'expiry_minutes': settings.DJANGO_SPIRE_AUTH_SMS_CODE_EXPIRY_MINUTES
        }
    )
