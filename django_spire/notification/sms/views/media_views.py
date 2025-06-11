import base64
import uuid

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django_spire.notification.sms.models import SmsTemporaryMedia


@csrf_exempt
def external_temporary_media_view(request, external_access_key: uuid.UUID) -> HttpResponse:
    temporary_media = SmsTemporaryMedia.objects.get(external_access_key=external_access_key)

    return HttpResponse(
        content=base64.b64decode(temporary_media.content),
        content_type=temporary_media.content_type
    )
