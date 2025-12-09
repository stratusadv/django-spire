from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class AuthUrlEndpointTestCase(BaseTestCase):
    pass

    # def test_login_view(self):
    #     response = self.client.get(reverse('user_account:authentication:admin:login'))
    #     assert response.status_code == 200
    #
    # def test_login_redirect_view(self):
    #     response = self.client.get(reverse('user_account:authentication:redirect:login'))
    #     assert response.status_code == 302
    #
    # def test_logout_redirect_view(self):
    #     response = self.client.get(reverse('user_account:authentication:redirect:logout'))
    #     assert response.status_code == 302
    #
    # def test_password_change_view(self):
    #     response = self.client.get(reverse('user_account:authentication:admin:password_change'))
    #     assert response.status_code == 200
    #
    # def password_set_form_view(self):
    #     response = self.client.get(reverse('user_account:authentication:admin:password_set_form'))
    #     assert response.status_code == 200
