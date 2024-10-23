from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class AuthUrlEndpointTestCase(BaseTestCase):
    def test_login_view(self):
        response = self.client.get(reverse('user_account:authentication:admin:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirect_view(self):
        response = self.client.get(reverse('user_account:authentication:redirect:login'))
        self.assertEqual(response.status_code, 302)

    def test_logout_redirect_view(self):
        response = self.client.get(reverse('user_account:authentication:redirect:logout'))
        self.assertEqual(response.status_code, 302)

    def test_password_change_view(self):
        response = self.client.get(reverse('user_account:authentication:admin:password_change'))
        self.assertEqual(response.status_code, 200)

    def password_set_form_view(self):
        response = self.client.get(reverse('user_account:authentication:admin:password_set_form'))
        self.assertEqual(response.status_code, 200)
