from __future__ import annotations

from unittest.mock import MagicMock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from django_spire.history.activity.admin import ActivityAdmin
from django_spire.history.activity.models import Activity
from django_spire.history.admin import HistoryEventAdmin
from django_spire.history.models import HistoryEvent
from django_spire.history.viewed.admin import ViewAdmin
from django_spire.history.viewed.models import Viewed


class TestActivityAdmin(TestCase):
    def setUp(self) -> None:
        self.site = AdminSite()
        self.admin = ActivityAdmin(Activity, self.site)

    def test_information_snippet_long(self) -> None:
        activity = MagicMock()
        activity.information = 'This is a very long information string that exceeds twenty characters'

        result = self.admin.information_snippet(activity)

        assert result.endswith('...')
        assert len(result) == 23

    def test_information_snippet_none(self) -> None:
        activity = MagicMock()
        activity.information = None

        result = self.admin.information_snippet(activity)

        assert result == 'No Information'

    def test_information_snippet_short(self) -> None:
        activity = MagicMock()
        activity.information = 'Short info'

        result = self.admin.information_snippet(activity)

        assert result == 'Short info'

    def test_list_display(self) -> None:
        assert 'id' in self.admin.list_display
        assert 'content_object_link' in self.admin.list_display
        assert 'verb' in self.admin.list_display
        assert 'user_link' in self.admin.list_display

    def test_list_filter(self) -> None:
        assert 'verb' in self.admin.list_filter
        assert 'created_datetime' in self.admin.list_filter

    def test_recipient_link_no_recipient(self) -> None:
        activity = MagicMock()
        activity.recipient = None

        result = self.admin.recipient_link(activity)

        assert result == 'No Recipient'


class TestHistoryEventAdmin(TestCase):
    def setUp(self) -> None:
        self.site = AdminSite()
        self.admin = HistoryEventAdmin(HistoryEvent, self.site)

    def test_list_display(self) -> None:
        assert 'id' in self.admin.list_display
        assert 'content_object_link' in self.admin.list_display
        assert 'content_type' in self.admin.list_display
        assert 'event_verbose' in self.admin.list_display

    def test_list_filter(self) -> None:
        assert 'event' in self.admin.list_filter
        assert 'created_datetime' in self.admin.list_filter


class TestViewedAdmin(TestCase):
    def setUp(self) -> None:
        self.site = AdminSite()
        self.admin = ViewAdmin(Viewed, self.site)

    def test_list_display(self) -> None:
        assert 'id' in self.admin.list_display
        assert 'content_object_link' in self.admin.list_display
        assert 'user_link' in self.admin.list_display
        assert 'created_datetime' in self.admin.list_display

    def test_list_filter(self) -> None:
        assert 'created_datetime' in self.admin.list_filter
