from __future__ import annotations

from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse

from django_spire.ai.sms.decorators import twilio_auth_required
from django_spire.ai.sms.intelligence.workflows.sms_conversation_workflow import sms_conversation_workflow
from django_spire.ai.sms.models import SmsConversation


@csrf_exempt
@require_POST
@twilio_auth_required
def webhook_view(request):
    from_number = request.POST.get('From', '')

    if len(from_number) < 11:
        return HttpResponseForbidden()

    body = request.POST.get('Body', '')
    message_sid = request.POST.get('MessageSid', '')

    conversation, created = SmsConversation.objects.get_or_create(
        phone_number=from_number
    )

    message = conversation.add_message(
        body=body,
        is_inbound=True,
        twilio_sid=message_sid,
    )

    try:

        sms_intel = sms_conversation_workflow(
            request=request,
            user_input=body,
            message_history=conversation.generate_message_history(),
            actor=from_number,
        )

        twiml_response = MessagingResponse()
        twiml_response.message(sms_intel.body)

        conversation.add_message(
            body=sms_intel.body,
            is_inbound=False,
            twilio_sid=message_sid,
            is_processed=True
        )

        message.is_processed = True
        message.save()

        return HttpResponse(twiml_response)

    except:
        raise



