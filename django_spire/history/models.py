from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import localtime

from django_spire.history.choices import HistoryEventChoices


class HistoryEvent(models.Model):
    content_type = models.ForeignKey(
        ContentType, 
        related_name='history_events', 
        related_query_name='history_event', 
        on_delete=models.CASCADE, 
        editable=False
    )
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    event = models.CharField(max_length=4, choices=HistoryEventChoices.choices)

    created_datetime = models.DateTimeField(default=localtime)

    def __str__(self) -> str:
        return f'{self.content_object} - {self.event_verbose}'

    @property
    def event_verbose(self) -> str:
        return dict(HistoryEventChoices.choices)[self.event]

    class Meta:
        db_table = 'django_spire_history_event'
        verbose_name = 'History Event'
        verbose_name_plural = 'History Events'

