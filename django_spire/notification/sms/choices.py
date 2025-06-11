from django.db import models


class SmsMediaContentTypeChoices(models.TextChoices):
    PNG = 'image/png'
    JPEG = 'image/jpeg'
