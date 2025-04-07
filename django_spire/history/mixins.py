from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import localtime
from typing_extensions import TYPE_CHECKING

from django_spire.history.choices import EventHistoryChoices
from django_spire.history.models import EventHistory

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class HistoryModelMixin(models.Model):
    is_active = models.BooleanField(default=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)

    event_history = GenericRelation(
        EventHistory,
        related_query_name='spire_event_history',
        editable=False
    )

    created_datetime = models.DateTimeField(default=localtime, editable=False)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)

        if self.pk:
            self.event_history.create(event=EventHistoryChoices.UPDATED)
        else:
            self.event_history.create(event=EventHistoryChoices.CREATED)

    def add_view(self, user: User) -> None:
        self.views.create(user=user)

    def is_viewed(self, user: User) -> None:
        return self.views.filter(user=user).exists()

    def set_active(self) -> None:
        self.is_active = True
        self.save()
        self.event_history.create(event=EventHistoryChoices.ACTIVE)

    def set_deleted(self) -> None:
        self.is_deleted = True
        self.save()
        self.event_history.create(event=EventHistoryChoices.DELETED)

    def set_inactive(self) -> None:
        self.is_active = False
        self.save()
        self.event_history.create(event=EventHistoryChoices.INACTIVE)

    def un_set_deleted(self) -> None:
        self.is_deleted = False
        self.save()
        self.event_history.create(event=EventHistoryChoices.UNDELETED)

    class Meta:
        abstract = True
