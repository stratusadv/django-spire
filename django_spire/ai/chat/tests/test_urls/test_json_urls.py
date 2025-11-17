from __future__ import annotations

from django_spire.ai.chat.tests.test_urls.factories import create_test_chat
from django_spire.core.tests.test_cases import BaseTestCase
from django.urls import reverse


class ChatJsonUrlTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.test_chat = create_test_chat(user=self.super_user)

    def test_delete_view_url_path(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:delete',
                kwargs={'pk': self.test_chat.pk}
            ),
            content_type='application/json'
        )

        assert response.status_code == 200
