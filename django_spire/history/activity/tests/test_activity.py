from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_spire.history.activity.models import Activity, ActivitySubscriber


class TestActivity(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            password='testpass'  # noqa: S106
        )
        self.content_type = ContentType.objects.get_for_model(User)

    def test_add_subscriber(self) -> None:
        activity = Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            verb='created',
            information='Test information'
        )

        subscriber = User.objects.create_user(
            username='subscriber',
            password='testpass'  # noqa: S106
        )

        activity.add_subscriber(subscriber)

        assert activity.subscribers.count() == 1

    def test_create_activity(self) -> None:
        activity = Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            verb='created',
            information='Test information'
        )

        assert activity.pk is not None
        assert activity.verb == 'created'
        assert activity.information == 'Test information'
        assert activity.content_object == self.user

    def test_create_activity_with_recipient(self) -> None:
        activity = Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            recipient=self.recipient,
            verb='assigned',
            information='Assigned to recipient'
        )

        assert activity.recipient == self.recipient

    def test_str_representation(self) -> None:
        activity = Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            verb='updated'
        )

        assert 'testuser' in str(activity)
        assert 'updated' in str(activity)


class TestActivitySubscriber(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.subscriber = User.objects.create_user(
            username='subscriber',
            password='testpass'  # noqa: S106
        )
        self.content_type = ContentType.objects.get_for_model(User)
        self.activity = Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            verb='created'
        )

    def test_create_activity_subscriber(self) -> None:
        activity_subscriber = ActivitySubscriber.objects.create(
            activity=self.activity,
            subscriber=self.subscriber
        )

        assert activity_subscriber.pk is not None
        assert activity_subscriber.activity == self.activity
        assert activity_subscriber.subscriber == self.subscriber

    def test_str_representation(self) -> None:
        activity_subscriber = ActivitySubscriber.objects.create(
            activity=self.activity,
            subscriber=self.subscriber
        )

        assert str(self.activity) in str(activity_subscriber)
        assert 'subscriber' in str(activity_subscriber)


class TestActivityQuerySet(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.content_type = ContentType.objects.get_for_model(User)

    def test_prefetch_user(self) -> None:
        Activity.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user,
            verb='created'
        )

        activities = Activity.objects.prefetch_user()

        assert activities.count() == 1


class TestAddFormActivity(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',  # noqa: S106
            first_name='Test',
            last_name='User'
        )
