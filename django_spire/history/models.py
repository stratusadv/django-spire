from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import localtime

from django_spire.history.querysets import ActivityQuerySet


EVENT_HISTORY_CHOICES = (
    ('crea', 'Created'),
    ('upda', 'Updated'),
    ('acti', 'Active'),
    ('inac', 'Inactive'),
    ('dele', 'Deleted'),
    ('unde', 'Un-Deleted'),
)


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


class EventHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    event = models.CharField(max_length=4, choices=EVENT_HISTORY_CHOICES, default='upda')

    created_datetime = models.DateTimeField(default=localtime)

    def __str__(self) -> str:
        return f'{self.content_object} - {self.event_verbose}'

    class Meta:
        verbose_name = 'Event History'
        verbose_name_plural = 'Event History'

    @property
    def event_verbose(self) -> str:
        return dict(EVENT_HISTORY_CHOICES)[self.event]


class View(models.Model):
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
        verbose_name = 'View'
        verbose_name_plural = 'Views'
