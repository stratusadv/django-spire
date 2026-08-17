from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.history.activity.models import Activity, ActivitySubscriber

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ActivityMixin(models.Model):
    activities = GenericRelation(Activity, related_query_name='activity', editable=False)

    class Meta:
        abstract = True

    def add_activity(
        self,
        user: User,
        verb: str,
        information: str,
        recipient: User = None,
        subscribers: list[User] | None = None,
    ) -> Activity:

        activity = self.activities.create(
            user=user,
            verb=verb,
            information=information,
            recipient=recipient,
        )

        if subscribers:
            subscriber_list = [
                ActivitySubscriber(activity=activity, subscriber=subscriber)
                for subscriber in subscribers
            ]

            ActivitySubscriber.objects.bulk_create(subscriber_list)

        return activity

    @property
    def creator(self) -> User:
        return self.activities.earliest('created_datetime').user
