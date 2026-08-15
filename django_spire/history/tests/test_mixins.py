from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.test import TestCase

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.choices import HistoryEventChoices
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.viewed.mixins import ViewedModelMixin

from test_project.app.task.models import Task


class TestActivityMixin(TestCase):
    def test_activities_field_exists(self) -> None:
        assert hasattr(ActivityMixin, 'activities')

    def test_activities_is_generic_relation(self) -> None:
        field = ActivityMixin._meta.get_field('activities')
        assert isinstance(field, GenericRelation)

    def test_creator_property_exists(self) -> None:
        assert hasattr(ActivityMixin, 'creator')

    def test_is_abstract(self) -> None:
        assert ActivityMixin._meta.abstract is True


class TestHistoryModelMixin(TestCase):
    def test_created_datetime_field_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'created_datetime')

    def test_history_events_field_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'history_events')

    def test_history_events_is_generic_relation(self) -> None:
        field = HistoryModelMixin._meta.get_field('history_events')
        assert isinstance(field, GenericRelation)

    def test_is_abstract(self) -> None:
        assert HistoryModelMixin._meta.abstract is True

    def test_is_active_field_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'is_active')

    def test_is_deleted_field_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'is_deleted')

    def test_set_active_method_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'set_active')
        assert callable(HistoryModelMixin.set_active)

    def test_set_deleted_method_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'set_deleted')
        assert callable(HistoryModelMixin.set_deleted)

    def test_set_inactive_method_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'set_inactive')
        assert callable(HistoryModelMixin.set_inactive)

    def test_un_set_deleted_method_exists(self) -> None:
        assert hasattr(HistoryModelMixin, 'un_set_deleted')
        assert callable(HistoryModelMixin.un_set_deleted)


class TestHistoryModelMixinEvents(TestCase):
    def test_create_logs_created_event(self) -> None:
        task = Task.objects.create(name='One')

        events = task.history_events.all()

        assert events.count() == 1
        assert events.first().event == HistoryEventChoices.CREATED

    def test_save_new_instance_logs_created_event(self) -> None:
        task = Task(name='Unsaved')
        task.save()

        assert task.history_events.filter(event=HistoryEventChoices.CREATED).count() == 1
        assert task.history_events.filter(event=HistoryEventChoices.UPDATED).count() == 0

    def test_update_logs_updated_event(self) -> None:
        task = Task.objects.create(name='One')

        task.name = 'Renamed'
        task.save()

        assert task.history_events.filter(event=HistoryEventChoices.CREATED).count() == 1
        assert task.history_events.filter(event=HistoryEventChoices.UPDATED).count() == 1

    def test_reloaded_instance_save_logs_updated_event(self) -> None:
        task = Task.objects.create(name='One')
        reloaded_task = Task.objects.get(pk=task.pk)

        reloaded_task.save()

        assert reloaded_task.history_events.filter(event=HistoryEventChoices.UPDATED).count() == 1


class TestViewedModelMixin(TestCase):
    def test_add_view_method_exists(self) -> None:
        assert hasattr(ViewedModelMixin, 'add_view')
        assert callable(ViewedModelMixin.add_view)

    def test_is_abstract(self) -> None:
        assert ViewedModelMixin._meta.abstract is True

    def test_is_viewed_method_exists(self) -> None:
        assert hasattr(ViewedModelMixin, 'is_viewed')
        assert callable(ViewedModelMixin.is_viewed)

    def test_views_field_exists(self) -> None:
        assert hasattr(ViewedModelMixin, 'views')

    def test_views_is_generic_relation(self) -> None:
        field = ViewedModelMixin._meta.get_field('views')
        assert isinstance(field, GenericRelation)
