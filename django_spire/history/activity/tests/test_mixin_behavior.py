from __future__ import annotations

import pytest

from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import DataError, transaction
from django.test import TestCase
from django.utils.timezone import localtime

from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.models import Activity, ActivitySubscriber

from test_project.app.task.models import Task


class ActivityMixinTestCase(TestCase):
    def setUp(self) -> None:
        self.user = AuthUser.objects.create_user(
            username='mixinactor',
            first_name='Mixin',
            last_name='Actor',
        )

        self.task = Task.objects.create(name='One')

    def tearDown(self) -> None:
        set_current_user(None)


class TestAddActivity(ActivityMixinTestCase):
    def test_returns_persisted_activity(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert activity.pk is not None
        assert Activity.objects.filter(pk=activity.pk).exists()

    def test_stores_verb_and_information(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert activity.verb == 'archived'
        assert activity.information == 'Archived.'
        assert activity.user == self.user

    def test_stores_content_type_and_object_id(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert activity.content_type == ContentType.objects.get_for_model(Task)
        assert activity.object_id == self.task.pk
        assert activity.content_object == self.task

    def test_stores_recipient(self) -> None:
        recipient = AuthUser.objects.create_user(username='mixinrecipient')

        activity = self.task.add_activity(
            user=self.user,
            verb='assigned',
            information='Assigned.',
            recipient=recipient,
        )

        assert activity.recipient == recipient

    def test_recipient_defaults_to_null(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert activity.recipient is None

    def test_subscribers_create_subscriber_rows(self) -> None:
        subscriber_one = AuthUser.objects.create_user(username='mixinsubone')
        subscriber_two = AuthUser.objects.create_user(username='mixinsubtwo')
        subscribers = [subscriber_one, subscriber_two]

        activity = self.task.add_activity(
            user=self.user,
            verb='archived',
            information='Archived.',
            subscribers=subscribers,
        )

        subscriber_pks = set(activity.subscribers.values_list('subscriber_id', flat=True))

        assert activity.subscribers.count() == 2
        assert subscriber_pks == {subscriber_one.pk, subscriber_two.pk}

    def test_without_subscribers_creates_no_subscriber_rows(self) -> None:
        self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert ActivitySubscriber.objects.count() == 0

    def test_empty_subscriber_list_creates_no_subscriber_rows(self) -> None:
        self.task.add_activity(
            user=self.user,
            verb='archived',
            information='Archived.',
            subscribers=[],
        )

        assert ActivitySubscriber.objects.count() == 0


class TestCreatorProperty(ActivityMixinTestCase):
    def test_returns_the_earliest_activity_user(self) -> None:
        other_user = AuthUser.objects.create_user(username='mixinlateractor')

        first = self.task.add_activity(user=self.user, verb='created', information='Created.')
        self.task.add_activity(user=other_user, verb='updated', information='Updated.')

        older_datetime = localtime() - timedelta(days=1)
        Activity.objects.filter(pk=first.pk).update(created_datetime=older_datetime)

        assert self.task.creator == self.user

    def test_ignores_activities_of_other_objects(self) -> None:
        other_task = Task.objects.create(name='Two')
        other_user = AuthUser.objects.create_user(username='mixinothercreator')

        older_datetime = localtime() - timedelta(days=1)

        other = other_task.add_activity(user=other_user, verb='created', information='Created.')
        Activity.objects.filter(pk=other.pk).update(created_datetime=older_datetime)

        self.task.add_activity(user=self.user, verb='created', information='Created.')

        assert self.task.creator == self.user

    def test_without_activities_raises_does_not_exist(self) -> None:
        with pytest.raises(Activity.DoesNotExist):
            _ = self.task.creator

    def test_reports_the_signal_actor_after_a_plain_create(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='Two')

        assert task.creator == self.user


class TestActivityModelBehavior(ActivityMixinTestCase):
    def test_activity_str_names_the_user_and_verb(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert str(activity) == f'{self.user} - archived'

    def test_activity_subscriber_str_names_the_activity(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')
        activity.add_subscriber(self.user)

        subscriber = ActivitySubscriber.objects.get(activity=activity)

        assert str(subscriber) == f'{activity} - {self.user}'

    def test_add_subscriber_creates_a_row(self) -> None:
        activity = self.task.add_activity(user=self.user, verb='archived', information='Archived.')

        activity.add_subscriber(self.user)

        assert activity.subscribers.count() == 1
        assert activity.subscribers.first().subscriber == self.user

    def test_newest_activity_is_ordered_first(self) -> None:
        set_current_user(self.user)

        self.task.name = 'One Renamed'
        self.task.save()
        self.task.set_deleted()

        assert Activity.objects.first().verb == 'deleted'


class TestActivityRelationQueries(ActivityMixinTestCase):
    def test_generic_relation_filters_owning_objects(self) -> None:
        self.task.add_activity(user=self.user, verb='archived', information='Archived.')
        Task.objects.create(name='Two')

        matches = Task.objects.filter(activities__verb='archived')

        assert matches.count() == 1
        assert matches.first() == self.task

    def test_signal_rows_are_reachable_through_the_relation(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='Two')

        assert task.activities.count() == 1
        assert task.activities.first().verb == 'created'

    def test_prefetch_user_returns_the_same_rows(self) -> None:
        set_current_user(self.user)

        Task.objects.create(name='Two')

        assert Activity.objects.prefetch_user().count() == 1
        assert Activity.objects.prefetch_user().first().user == self.user


class TestActivityStorageConstraints(ActivityMixinTestCase):
    def test_object_id_supports_the_largest_positive_integer_primary_key(self) -> None:
        set_current_user(self.user)

        task = Task(pk=2147483647, name='At The Ceiling')
        task.save()

        assert Activity.objects.filter(object_id=2147483647).count() == 1

    def test_primary_key_beyond_the_object_id_range_fails_the_write(self) -> None:
        set_current_user(self.user)

        over_ceiling_task = Task(pk=2147483648, name='Over The Ceiling')

        with pytest.raises(DataError), transaction.atomic():
            over_ceiling_task.save()

        assert Task.objects.filter(pk=2147483648).count() == 0

    def test_deleting_the_actor_removes_their_activity_rows(self) -> None:
        set_current_user(self.user)

        Task.objects.create(name='Two')

        assert Activity.objects.count() == 1

        set_current_user(None)
        self.user.delete()

        assert Activity.objects.count() == 0

    def test_deleting_a_recipient_removes_the_activity_row(self) -> None:
        recipient = AuthUser.objects.create_user(username='mixindoomedrecipient')

        self.task.add_activity(
            user=self.user,
            verb='assigned',
            information='Assigned.',
            recipient=recipient,
        )

        assert Activity.objects.count() == 1

        recipient.delete()

        assert Activity.objects.count() == 0
