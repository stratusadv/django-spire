from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.tests.factories import create_test_app_notification


class AppNotificationPageViewsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app_notification = create_test_app_notification(user=self.super_user)

    def test_app_notification_list_view_status_code(self):
        response = self.client.get(
            reverse('django_spire:notification:app:page:list')
        )

        assert response.status_code == 200
