from django_spire.notification.sms.models import SmsMediaTypeChoices

SMS_TEMPORARY_MEDIA_TYPES_MAP = {
    'image/jpeg': SmsMediaTypeChoices.JPEG,
    'image/png': SmsMediaTypeChoices.PNG
}
