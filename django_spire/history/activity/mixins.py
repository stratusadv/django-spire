from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_spire.history.activity.models import Activity, ActivitySubscriber


class ActivityMixin(models.Model):
    activities = GenericRelation(
        Activity,
        related_query_name='activity',
        editable=False
    )

    def add_activity(
            self,
            user: User,
            verb: str,
            information: str,
            recipient: User = None,
            subscribers: list[User] | None = None
    ) -> Activity:

        activity = self.activities.create(
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

    @property
    def creator(self) -> User:
        return self.activities.earliest('date_time_entered').user

    class Meta:
        abstract = True
