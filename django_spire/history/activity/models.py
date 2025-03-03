from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import localtime

from django_spire.history.activity.querysets import ActivityQuerySet


class ActivityLog(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(
        User,
        related_name='users',
        related_query_name='user',
        on_delete=models.CASCADE,
        editable=False
    )

    recipient = models.ForeignKey(
        User,
        related_name='actors',
        related_query_name='actor',
        on_delete=models.CASCADE,
        editable=False,
        blank=True,
        null=True
    )

    verb = models.CharField(max_length=64)
    information = models.TextField(null=True, blank=True)

    created_datetime = models.DateTimeField(default=localtime)

    objects = ActivityQuerySet.as_manager()

    def __str__(self):
        return f'{self.user} - {self.verb}'

    def add_subscriber(self, subscriber: User) -> None:
        self.subscribers.create(
            user=subscriber
        )

    class Meta:
        verbose_name = 'Activities'
        verbose_name_plural = 'Activities'
        ordering = ['-created_datetime']


class ActivitySubscriber(models.Model):
    activity = models.ForeignKey(
        'spire_history.ActivityLog',
        on_delete=models.CASCADE,
        related_name='subscribers',
        related_query_name='subscriber'
    )

    subscriber = models.ForeignKey(
        User,
        related_name='activity_subscribers',
        related_query_name='activity_subscriber',
        on_delete=models.CASCADE,
        editable=False
    )

    created_datetime = models.DateTimeField(default=localtime)

    def __str__(self):
        return f'{self.activity} - {self.subscriber}'
