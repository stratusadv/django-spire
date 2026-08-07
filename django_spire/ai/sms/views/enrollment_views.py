from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django_spire.ai.sms.messaging import message_send, phone_number_normalize
from django_spire.ai.sms.models import SmsCodePurposeChoices, SmsPhoneNumber
from django_spire.ai.sms.throttling import throttle_allowed
from django_spire.conf import settings

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required
@require_POST
def enrollment_start_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = request.POST.get('phone_number', '')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return JsonResponse({'detail': 'invalid_phone_number'}, status=400)

    if not throttle_allowed(phone_number_normalized):
        return JsonResponse({'detail': 'throttled'}, status=429)

    existing = SmsPhoneNumber.objects.filter(phone_number=phone_number_normalized).first()

    if existing is not None and existing.user_id != request.user.id:
        return JsonResponse({'detail': 'phone_number_unavailable'}, status=400)

    if existing is None:
        phone_number = SmsPhoneNumber.objects.create(
            user=request.user,
            phone_number=phone_number_normalized,
        )
    else:
        phone_number = existing

    code = phone_number.code_issue(SmsCodePurposeChoices.ENROLLMENT)
    expiry_minutes = settings.DJANGO_SPIRE_AI_SMS_CODE_EXPIRY_MINUTES

    body = f'Your verification code is {code}. It expires in {expiry_minutes} minutes.'
    message_send(phone_number_normalized, body)

    return JsonResponse({'detail': 'verification_code_sent'})


@login_required
@require_POST
def enrollment_confirm_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = request.POST.get('phone_number', '')
    code = request.POST.get('code', '')

    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return JsonResponse({'detail': 'invalid_phone_number'}, status=400)

    phone_number = SmsPhoneNumber.objects.filter(
        phone_number=phone_number_normalized,
        user=request.user,
    ).first()

    if phone_number is None:
        return JsonResponse({'detail': 'phone_number_not_found'}, status=404)

    code_valid = phone_number.code_confirm(code, SmsCodePurposeChoices.ENROLLMENT)

    if not code_valid:
        return JsonResponse({'detail': 'invalid_code'}, status=400)

    phone_number.verified_mark()

    return JsonResponse({'detail': 'verified'})


@login_required
@require_POST
def session_code_view(request: WSGIRequest) -> JsonResponse:
    phone_number_raw = request.POST.get('phone_number', '')
    phone_number_normalized = phone_number_normalize(phone_number_raw)

    if phone_number_normalized is None:
        return JsonResponse({'detail': 'invalid_phone_number'}, status=400)

    phone_number = (
        SmsPhoneNumber.objects.verified_by_phone_number(phone_number_normalized)
        .filter(user=request.user)
        .first()
    )

    if phone_number is None:
        return JsonResponse({'detail': 'phone_number_not_found'}, status=404)

    code = phone_number.code_issue(SmsCodePurposeChoices.SESSION)
    expiry_minutes = settings.DJANGO_SPIRE_AI_SMS_CODE_EXPIRY_MINUTES

    response_data = {
        'code': code,
        'expiry_minutes': expiry_minutes,
    }

    return JsonResponse(response_data)
