from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from django_spire.ai.sms.models import SmsConversation, SmsMessage


@csrf_exempt
@require_POST
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

    # Create a response
    # response = process_message(conversation, message)

    # return HttpResponse(response)