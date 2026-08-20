from __future__ import annotations

from django.urls import reverse

from django_spire.auth.sms.models import AuthSms
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class KnowledgePageUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()

    def test_home_view_url_path(self):
        response = self.client.get(reverse('django_spire:knowledge:page:home'))
        assert response.status_code == 200

    def test_home_view_contains_collections(self):
        response = self.client.get(reverse('django_spire:knowledge:page:home'))
        assert 'collections' in response.context

    def test_home_view_shows_verification_content_when_unverified(self):
        response = self.client.get(reverse('django_spire:knowledge:page:home'))
        assert 'Verify Your Phone Number' in response.content.decode()

    def test_home_view_shows_session_content_when_verified(self):
        AuthSms.objects.create(
            user=self.super_user, phone_number='+15555550123', is_verified=True
        )
        response = self.client.get(reverse('django_spire:knowledge:page:home'))
        content = response.content.decode()
        assert 'Chat From Your Phone' in content
        assert 'Get a Code' in content
