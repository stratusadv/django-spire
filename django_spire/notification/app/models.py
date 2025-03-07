from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey

from django_spire.history.viewed.mixins import ViewedModelMixin
from django_spire.notification.models import Notification

class AppNotification(ViewedModelMixin):
    notification = models.ForeignKey(Notification, editable=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.notification.title} - {self.email}'

