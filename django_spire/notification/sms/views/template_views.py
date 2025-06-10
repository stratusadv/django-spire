import uuid

from django.template.response import TemplateResponse

from django_spire.notification.sms.models import SmsTemporaryMedia


def temporary_media_template_view(request, external_access_key: uuid.UUID) -> TemplateResponse:
    temporary_media = SmsTemporaryMedia.objects.get(external_access_key=external_access_key)

    return TemplateResponse(
        request,
        context={},
        template='django_spire/notification/sms/page/temporary_media_page.html',
    )
