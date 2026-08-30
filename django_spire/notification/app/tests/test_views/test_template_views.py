from __future__ import annotations

import json

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.tests.factories import create_test_app_notification


class AppNotificationTemplateViewsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.app_notification = create_test_app_notification(user=self.super_user)
        self.other_app_notification = create_test_app_notification(user=self.super_user)

    def test_render_templates_view_renders_only_requested_ids(self):
        payload = {'ids': [self.app_notification.pk]}

        response = self.client.post(
            reverse('django_spire:notification:app:template:render_templates'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert list(response.json().keys()) == [str(self.app_notification.pk)]

    def test_render_templates_view_returns_empty_without_ids(self):
        payload = {'ids': []}

        response = self.client.post(
            reverse('django_spire:notification:app:template:render_templates'),
            data=json.dumps(payload),
            content_type='application/json',
        )

        assert response.status_code == 200
        assert response.json() == {}
