from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import localtime

from django_spire.history.choices import EventHistoryChoices


class EventHistory(models.Model):
    content_type = models.ForeignKey(ContentType, related_name='django_spire_eventhistory', on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    event = models.CharField(max_length=4, choices=EventHistoryChoices.choices, default='upda')

    created_datetime = models.DateTimeField(default=localtime)

    def __str__(self) -> str:
        return f'{self.content_object} - {self.event_verbose}'

    class Meta:
        db_table = 'django_spire_history_event_history'
        verbose_name = 'Event History'
        verbose_name_plural = 'Event History'

    @property
    def event_verbose(self) -> str:
        return dict(EventHistoryChoices.choices)[self.event]
