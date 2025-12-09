from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.tests.factories import create_test_app_notification


class AppNotificationJsonViewsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app_notification = create_test_app_notification(user=self.super_user)

    def test_check_new_notifications_ajax_view(self):
        response = self.client.get(
            reverse('django_spire:notification:app:json:check_new')
        )

        assert response.status_code == 200
        assert 'has_new_notifications' in response.json()

    def test_check_new_notifications_returns_true_when_unviewed(self):
        response = self.client.get(
            reverse('django_spire:notification:app:json:check_new')
        )

        data = response.json()
        assert data['has_new_notifications'] is True

    def test_set_notifications_as_viewed_ajax_view(self):
        response = self.client.get(
            reverse('django_spire:notification:app:json:set_viewed')
        )

        assert response.status_code == 200
        assert response.json()['status'] == 200

    def test_set_notifications_as_viewed_marks_as_viewed(self):
        self.client.get(
            reverse('django_spire:notification:app:json:set_viewed')
        )

        check_response = self.client.get(
            reverse('django_spire:notification:app:json:check_new')
        )

        data = check_response.json()
        assert data['has_new_notifications'] is False
