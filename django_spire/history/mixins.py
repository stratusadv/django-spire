from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.timezone import localtime

from django_spire.history.models import (
    ActivityLog,
    ActivitySubscriber,
    EventHistory,
    View
)

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ActivityLogMixin(models.Model):
    activity_log = GenericRelation(
        ActivityLog,
        related_query_name='activity_log',
        editable=False
    )

    def add_activity(
            self,
            user: User,
            verb: str,
            information: str,
            recipient: User = None,
            subscribers: list[User] | None = None
    ) -> ActivityLog:

        activity = self.activity_log.create(
            user=user,
            verb=verb,
            information=information,
            recipient=recipient
        )

        if subscribers:
            subscriber_list = [
                ActivitySubscriber(user=subscriber, activity=activity)
                for subscriber in subscribers
            ]

            ActivitySubscriber.objects.bulk_create(subscriber_list)

        return activity

    class Meta:
        abstract = True


class HistoryModelMixin(ActivityLogMixin):
    is_active = models.BooleanField(default=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)

    activity_log = GenericRelation(ActivityLog, related_query_name='activity_log', editable=False)
    event_history = GenericRelation(EventHistory, related_query_name='event_history', editable=False)
    views = GenericRelation(View, related_query_name='view', editable=False)

    created_datetime = models.DateTimeField(default=localtime, editable=False)

    def add_view(self, user: User) -> None:
        self.views.create(user=user)

    def is_viewed(self, user: User) -> None:
        return self.views.filter(user=user).exists()

    @property
    def creator(self) -> User:
        return self.activity_log.earliest('date_time_entered').user

    def save(self, *args, **kwargs) -> None:
        created = self.pk is None
        super().save(*args, **kwargs)

        if created:
            self.event_history.create(event='crea')
        else:
            self.event_history.create(event='upda')

    def set_active(self) -> None:
        self.is_active = True
        self.save()
        self.event_history.create(event='acti')

    def set_deleted(self) -> None:
        self.is_deleted = True
        self.save()
        self.event_history.create(event='dele')

    def set_inactive(self) -> None:
        self.is_active = False
        self.save()
        self.event_history.create(event='inac')

    def un_set_deleted(self) -> None:
        self.is_deleted = False
        self.save()
        self.event_history.create(event='unde')

    class Meta:
        abstract = True
