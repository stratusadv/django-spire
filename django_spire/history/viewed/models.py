from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import localtime


class Viewed(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        related_name='views',
        related_query_name='view'
    )

    created_datetime = models.DateTimeField(default=localtime, editable=False)

    def __str__(self):
        return f'{self.user} viewed {self.content_object} at {self.created_datetime}'

    class Meta:
        db_table = 'django_spire_history_viewed'
        verbose_name = 'Viewed'
        verbose_name_plural = 'Views'
