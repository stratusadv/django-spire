from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.notification.models import Notification


class DjangoSpireNotificationMixin(models.Model):
    notifications = GenericRelation(Notification)

    class Meta:
        abstract = True
