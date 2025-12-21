from __future__ import annotations

import json

from django.urls import reverse

from django_spire.ai.chat.tests.test_urls.factories import create_test_chat
from django_spire.core.tests.test_cases import BaseTestCase


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

    def test_delete_view_success_response(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:delete',
                kwargs={'pk': self.test_chat.pk}
            ),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'success'
        assert 'deleted' in data['message'].lower()

    def test_delete_view_sets_deleted_flag(self) -> None:
        self.client.post(
            reverse(
                'django_spire:ai:chat:json:delete',
                kwargs={'pk': self.test_chat.pk}
            ),
            content_type='application/json'
        )

        self.test_chat.refresh_from_db()

        assert self.test_chat.is_deleted

    def test_delete_view_nonexistent_chat(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:delete',
                kwargs={'pk': 99999}
            ),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'error'

    def test_rename_view_url_path(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': 'New Chat Name'}),
            content_type='application/json'
        )

        assert response.status_code == 200

    def test_rename_view_success_response(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': 'Updated Name'}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'success'

    def test_rename_view_updates_name(self) -> None:
        new_name = 'Brand New Name'

        self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': new_name}),
            content_type='application/json'
        )

        self.test_chat.refresh_from_db()

        assert self.test_chat.name == new_name

    def test_rename_view_empty_name(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': ''}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'error'

    def test_rename_view_name_too_long(self) -> None:
        long_name = 'A' * 200

        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': long_name}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'error'

    def test_rename_view_nonexistent_chat(self) -> None:
        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': 99999}
            ),
            data=json.dumps({'new_name': 'New Name'}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'error'

    def test_rename_view_max_length_name(self) -> None:
        max_length_name = 'A' * 128

        response = self.client.post(
            reverse(
                'django_spire:ai:chat:json:rename',
                kwargs={'pk': self.test_chat.pk}
            ),
            data=json.dumps({'new_name': max_length_name}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'success'

        self.test_chat.refresh_from_db()
        assert self.test_chat.name == max_length_name


class ChatJsonUrlAdditionalTests(BaseTestCase):
    def test_delete_multiple_chats(self) -> None:
        chat1 = create_test_chat(user=self.super_user)
        chat2 = create_test_chat(user=self.super_user)

        self.client.post(
            reverse('django_spire:ai:chat:json:delete', kwargs={'pk': chat1.pk}),
            content_type='application/json'
        )

        self.client.post(
            reverse('django_spire:ai:chat:json:delete', kwargs={'pk': chat2.pk}),
            content_type='application/json'
        )

        chat1.refresh_from_db()
        chat2.refresh_from_db()

        assert chat1.is_deleted
        assert chat2.is_deleted

    def test_rename_with_special_characters(self) -> None:
        chat = create_test_chat(user=self.super_user)
        special_name = "Chat with 'quotes' and \"double quotes\""

        response = self.client.post(
            reverse('django_spire:ai:chat:json:rename', kwargs={'pk': chat.pk}),
            data=json.dumps({'new_name': special_name}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'success'

    def test_rename_with_unicode(self) -> None:
        chat = create_test_chat(user=self.super_user)
        unicode_name = 'Chat 日本語 🎉'

        response = self.client.post(
            reverse('django_spire:ai:chat:json:rename', kwargs={'pk': chat.pk}),
            data=json.dumps({'new_name': unicode_name}),
            content_type='application/json'
        )

        data = response.json()

        assert data['type'] == 'success'

        chat.refresh_from_db()
        assert chat.name == unicode_name
