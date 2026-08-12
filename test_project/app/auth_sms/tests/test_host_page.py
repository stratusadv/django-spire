from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase

from django_spire.auth.sms.models import AuthSms

HOST_URL = 'auth_sms:page:phone_verification'


class AuthSmsHostPageTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(HOST_URL)

    def test_page_requires_login(self) -> None:
        self.client.logout()

        response = self.client.get(self.url)

        assert response.status_code == 302

    def test_page_renders_when_logged_in(self) -> None:
        response = self.client.get(self.url)

        assert response.status_code == 200

    def test_page_renders_side_navigation_link(self) -> None:
        response = self.client.get(self.url)
        content = response.content.decode()

        expected_href = reverse('auth_sms:page:phone_verification')

        assert expected_href in content
        assert 'Phone Verification' in content

    def test_page_context_has_no_sms_auth_when_none_exists(self) -> None:
        response = self.client.get(self.url)

        assert response.context['sms_auth'] is None

    def test_page_context_has_sms_auth(self) -> None:
        sms_auth = AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        response = self.client.get(self.url)

        assert response.context['sms_auth'] == sms_auth

    def test_page_renders_verified_state(self) -> None:
        AuthSms.objects.create(user=self.super_user, phone_number='+15551234567', is_verified=True)

        response = self.client.get(self.url)
        content = response.content.decode()

        assert 'Verified' in content

    def test_page_renders_unverified_state(self) -> None:
        AuthSms.objects.create(user=self.super_user, phone_number='+15551234567')

        response = self.client.get(self.url)
        content = response.content.decode()

        assert 'Not Verified' in content
