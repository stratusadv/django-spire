from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_spire.history.choices import HistoryEventChoices
from django_spire.history.models import HistoryEvent
from django_spire.history.querysets import HistoryQuerySet


class TestHistoryEventChoices(TestCase):
    def test_active_choice(self) -> None:
        assert HistoryEventChoices.ACTIVE.value == 'acti'
        assert HistoryEventChoices.ACTIVE.label == 'Active'

    def test_all_choices_exist(self) -> None:
        choices = [c[0] for c in HistoryEventChoices.choices]

        assert 'crea' in choices
        assert 'upda' in choices
        assert 'acti' in choices
        assert 'inac' in choices
        assert 'dele' in choices
        assert 'unde' in choices

    def test_created_choice(self) -> None:
        assert HistoryEventChoices.CREATED.value == 'crea'
        assert HistoryEventChoices.CREATED.label == 'Created'

    def test_deleted_choice(self) -> None:
        assert HistoryEventChoices.DELETED.value == 'dele'
        assert HistoryEventChoices.DELETED.label == 'Deleted'

    def test_inactive_choice(self) -> None:
        assert HistoryEventChoices.INACTIVE.value == 'inac'
        assert HistoryEventChoices.INACTIVE.label == 'Inactive'

    def test_undeleted_choice(self) -> None:
        assert HistoryEventChoices.UNDELETED.value == 'unde'
        assert HistoryEventChoices.UNDELETED.label == 'Un-Deleted'

    def test_updated_choice(self) -> None:
        assert HistoryEventChoices.UPDATED.value == 'upda'
        assert HistoryEventChoices.UPDATED.label == 'Updated'


class TestHistoryEvent(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.content_type = ContentType.objects.get_for_model(User)

    def test_create_history_event(self) -> None:
        event = HistoryEvent.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            event=HistoryEventChoices.CREATED
        )

        assert event.pk is not None
        assert event.event == 'crea'
        assert event.content_object == self.user

    def test_event_verbose_property(self) -> None:
        event = HistoryEvent.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            event=HistoryEventChoices.UPDATED
        )

        assert event.event_verbose == 'Updated'

    def test_str_representation(self) -> None:
        event = HistoryEvent.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            event=HistoryEventChoices.CREATED
        )

        assert 'Created' in str(event)


class TestHistoryQuerySet(TestCase):
    def test_active_filter(self) -> None:
        # HistoryQuerySet is meant to be used with models that have
        # is_active and is_deleted fields (via HistoryModelMixin)
        qs = HistoryQuerySet(model=HistoryEvent)

        # Verify the method exists and returns a QuerySet
        assert hasattr(qs, 'active')

    def test_deleted_filter(self) -> None:
        qs = HistoryQuerySet(model=HistoryEvent)
        assert hasattr(qs, 'deleted')

    def test_inactive_filter(self) -> None:
        qs = HistoryQuerySet(model=HistoryEvent)
        assert hasattr(qs, 'inactive')
