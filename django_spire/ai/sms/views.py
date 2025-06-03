from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from django_spire.ai.sms.decorators import twilio_auth_required
from django_spire.ai.sms.models import SmsConversation, SmsMessage
from django_spire.ai.sms.tools import sms_workflow_process


@csrf_exempt
@require_POST
@twilio_auth_required
def webhook_view(request):
    from_number = request.POST.get('From', '')
    body = request.POST.get('Body', '')
    message_sid = request.POST.get('MessageSid', '')

    conversation, created = SmsConversation.objects.get_or_create(
        phone_number=from_number
    )

    message = conversation.add_message(body=body, is_inbound=True)
    message.twilio_sid = message_sid
    message.save()

    response = process_message(request, conversation, message)

    return HttpResponse(response)


def process_message(request, conversation, message):
    message_intel = sms_workflow_process(
        request,
        message,
        message_history=conversation.generate_message_history(),
    )

    response_body = f"You said: {message_intel.text}"

    twiml_response = MessagingResponse()
    twiml_response.message(response_body)

    conversation.add_message(body=response_body, is_inbound=False)

    return twiml_response


def send_sms(to_number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    twilio_message = client.messages.create(
        to=to_number,
        from_=settings.TWILIO_PHONE_NUMBER,
        body=body
    )

    conversation, created = SmsConversation.objects.get_or_create(
        phone_number=to_number
    )

    message = conversation.add_message(body=body, is_inbound=False)
    message.twilio_sid = twilio_message.sid
    message.save()

    return message