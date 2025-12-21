from __future__ import annotations

from django.contrib.admin.sites import AdminSite

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.admin import NotificationAdmin
from django_spire.notification.models import Notification
from django_spire.notification.tests.factories import create_test_notification


class NotificationAdminTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.site = AdminSite()
        self.admin = NotificationAdmin(Notification, self.site)
        self.notification = create_test_notification()

    def test_list_display(self):
        expected = (
            'id', 'title', 'type', 'user', 'view_body_snippet', 'url_link', 'status',
            'status_message', 'priority', 'sent_datetime', 'publish_datetime',
            'content_type', 'object_id', 'is_deleted'
        )
        assert self.admin.list_display == expected

    def test_list_filter(self):
        expected = ('type',)
        assert self.admin.list_filter == expected

    def test_search_fields(self):
        expected = ('id', 'title', 'type')
        assert self.admin.search_fields == expected

    def test_view_body_snippet_truncates_long_body(self):
        self.notification.body = 'A' * 50
        result = self.admin.view_body_snippet(self.notification)
        assert len(result) <= 23
        assert result.endswith('...')

    def test_view_body_snippet_short_body(self):
        self.notification.body = 'Short'
        result = self.admin.view_body_snippet(self.notification)
        assert result == 'Short'

    def test_url_link_with_url(self):
        self.notification.url = 'https://example.com'
        result = self.admin.url_link(self.notification)
        assert 'href="https://example.com"' in result
        assert 'Link' in result

    def test_url_link_without_url(self):
        self.notification.url = ''
        result = self.admin.url_link(self.notification)
        assert result == 'No URL'
