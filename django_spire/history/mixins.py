from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import localtime
from typing_extensions import TYPE_CHECKING

from django_spire.history.choices import HistoryEventChoices
from django_spire.history.models import HistoryEvent

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class HistoryModelMixin(models.Model):
    is_active = models.BooleanField(default=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)

    history_events = GenericRelation(
        HistoryEvent,
        related_query_name='history_event',
        editable=False
    )

    created_datetime = models.DateTimeField(default=localtime, editable=False)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if self.pk:
            self.history_events.create(event=HistoryEventChoices.UPDATED)
        else:
            self.history_events.create(event=HistoryEventChoices.CREATED)

    def set_active(self) -> None:
        self.is_active = True
        self.save()
        self.history_events.create(event=HistoryEventChoices.ACTIVE)

    def set_deleted(self) -> None:
        self.is_deleted = True
        self.save()
        self.history_events.create(event=HistoryEventChoices.DELETED)

    def set_inactive(self) -> None:
        self.is_active = False
        self.save()
        self.history_events.create(event=HistoryEventChoices.INACTIVE)

    def un_set_deleted(self) -> None:
        self.is_deleted = False
        self.save()
        self.history_events.create(event=HistoryEventChoices.UNDELETED)

    class Meta:
        abstract = True
