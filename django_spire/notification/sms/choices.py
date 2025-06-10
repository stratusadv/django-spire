from django.db import models


class SmsMediaTypeChoices(models.TextChoices):
    PNG = 'png'
    JPEG = 'jpeg'
