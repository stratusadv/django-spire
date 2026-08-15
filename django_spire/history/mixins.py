from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import localtime

from django_spire.history.activity.context import ACTIVITY_VERB_ATTRIBUTE
from django_spire.history.activity.enums import ActivityVerb
from django_spire.history.choices import HistoryEventChoices
from django_spire.history.models import HistoryEvent


class HistoryModelMixin(models.Model):
    is_active = models.BooleanField(default=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)

    history_events = GenericRelation(
        HistoryEvent, related_query_name='history_event', editable=False
    )

    created_datetime = models.DateTimeField(default=localtime, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        is_new_row = self._state.adding

        super().save(*args, **kwargs)

        if is_new_row:
            self.history_events.create(event=HistoryEventChoices.CREATED)
        else:
            self.history_events.create(event=HistoryEventChoices.UPDATED)

    def set_active(self) -> None:
        self.is_active = True
        self.save()
        self.history_events.create(event=HistoryEventChoices.ACTIVE)

    def set_deleted(self) -> None:
        was_deleted = self.is_deleted
        self.is_deleted = True

        if not was_deleted:
            setattr(self, ACTIVITY_VERB_ATTRIBUTE, ActivityVerb.DELETED)

        try:
            self.save()
        except Exception:
            self.is_deleted = was_deleted
            raise
        finally:
            self.__dict__.pop(ACTIVITY_VERB_ATTRIBUTE, None)

        self.history_events.create(event=HistoryEventChoices.DELETED)

    def set_inactive(self) -> None:
        self.is_active = False
        self.save()
        self.history_events.create(event=HistoryEventChoices.INACTIVE)

    def un_set_deleted(self) -> None:
        self.is_deleted = False
        self.save()
        self.history_events.create(event=HistoryEventChoices.UNDELETED)
