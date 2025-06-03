from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_spire.ai.sms.decorators import twilio_auth_required
from django_spire.ai.sms.models import SmsConversation
from django_spire.ai.sms.tools import process_message


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


