from __future__ import annotations

import base64

from io import BytesIO
from typing import TYPE_CHECKING

from PIL import Image

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django_spire.notification.sms.exceptions import SmsTemporaryMediaError
from django_spire.notification.sms.models import SmsTemporaryMedia

if TYPE_CHECKING:
    import uuid


@csrf_exempt
def external_temporary_media_view(request, external_access_key: uuid.UUID) -> HttpResponse:
    try:
        temporary_media = SmsTemporaryMedia.objects.get(external_access_key=external_access_key)
    except SmsTemporaryMedia.DoesNotExist:
        temporary_media = None

    if temporary_media is None or temporary_media.content == '':
        message = 'Content for Temporary Media cannot be empty'
        raise SmsTemporaryMediaError(message)

    image = Image.open(
        BytesIO(base64.b64decode(temporary_media.content))
    )
    image = image.convert('P', palette=Image.ADAPTIVE, colors=32)

    buffer = BytesIO()
    image.save(buffer, 'PNG')

    return HttpResponse(
        content=buffer.getvalue(),
        content_type=temporary_media.content_type,
    )
