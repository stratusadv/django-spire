import base64
import uuid
from io import BytesIO

from PIL import Image

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django_spire.notification.sms.models import SmsTemporaryMedia


@csrf_exempt
def external_temporary_media_view(request, external_access_key: uuid.UUID) -> HttpResponse:
    temporary_media = SmsTemporaryMedia.objects.get(external_access_key=external_access_key)

    image = Image.open(
        BytesIO(base64.b64decode(temporary_media.content))
    ).convert('P', palette=Image.ADAPTIVE, colors=32)

    image = image.resize((int(image.size[0]/2), int(image.size[1]/2)), resample=Image.Resampling.BICUBIC)

    buffer = BytesIO()
    image.save(buffer, 'PNG')

    return HttpResponse(
        content=buffer.getvalue(),
        content_type=temporary_media.content_type
    )
