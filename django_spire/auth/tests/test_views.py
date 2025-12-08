from __future__ import annotations

from django.urls import reverse

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class LoginViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.logout()
        self.user = create_user(username='testuser', email='test@example.com')
        self.user.set_password('testpassword123')
        self.user.save()

    def test_login_page_loads(self) -> None:
        response = self.client.get(reverse('django_spire:auth:admin:login'))
        assert response.status_code == 200

    def test_login_with_valid_credentials(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'testpassword123'}
        )
        assert response.status_code == 302

    def test_login_with_invalid_credentials(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'wrongpassword'}
        )
        assert response.status_code == 200

    def test_login_with_nonexistent_user(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'nonexistent', 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_empty_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': '', 'password': 'testpassword123'}
        )
        assert response.status_code == 200

    def test_login_with_empty_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': ''}
        )
        assert response.status_code == 200

    def test_login_inactive_user(self) -> None:
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'testpassword123'}
        )
        assert response.status_code == 200


class PasswordChangeViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')
        self.user.set_password('oldpassword123')
        self.user.save()
        self.client.force_login(self.user)

    def test_password_change_page_loads(self) -> None:
        response = self.client.get(reverse('django_spire:auth:admin:password_change'))
        assert response.status_code == 200

    def test_password_change_success(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'newpassword456',
                'new_password2': 'newpassword456'
            }
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.check_password('newpassword456') is True

    def test_password_change_wrong_old_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'wrongoldpassword',
                'new_password1': 'newpassword456',
                'new_password2': 'newpassword456'
            }
        )
        assert response.status_code == 200
        self.user.refresh_from_db()
        assert self.user.check_password('oldpassword123') is True

    def test_password_change_mismatched_passwords(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'newpassword456',
                'new_password2': 'differentpassword789'
            }
        )
        assert response.status_code == 200

    def test_password_change_empty_new_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': '',
                'new_password2': ''
            }
        )
        assert response.status_code == 200

    def test_password_change_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(reverse('django_spire:auth:admin:password_change'))
        assert response.status_code == 302


class PasswordChangeDoneViewTestCase(BaseTestCase):
    def test_password_change_done_page_loads(self) -> None:
        response = self.client.get(reverse('django_spire:auth:admin:password_change_done'))
        assert response.status_code == 200


class PasswordResetViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser', email='test@example.com')

    def test_password_reset_page_loads(self) -> None:
        response = self.client.get(reverse('django_spire:auth:admin:password_reset'))
        assert response.status_code == 200

    def test_password_reset_with_valid_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'test@example.com'}
        )
        assert response.status_code == 302

    def test_password_reset_with_nonexistent_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'nonexistent@example.com'}
        )
        assert response.status_code == 302

    def test_password_reset_with_empty_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': ''}
        )
        assert response.status_code == 200

    def test_password_reset_with_invalid_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'invalid-email'}
        )
        assert response.status_code == 200


class PasswordResetDoneViewTestCase(BaseTestCase):
    def test_password_reset_done_page_loads(self) -> None:
        response = self.client.get(reverse('django_spire:auth:admin:password_reset_done'))
        assert response.status_code == 200


class LogoutRedirectViewTestCase(BaseTestCase):
    def test_logout_redirects(self) -> None:
        response = self.client.get(reverse('django_spire:auth:redirect:logout'))
        assert response.status_code == 302

    def test_logout_logs_out_user(self) -> None:
        self.client.get(reverse('django_spire:auth:redirect:logout'))
        response = self.client.get(reverse('django_spire:auth:admin:password_change'))
        assert response.status_code != 200

    def test_logout_redirects_to_login(self) -> None:
        response = self.client.get(reverse('django_spire:auth:redirect:logout'))
        assert 'login' in response.url.lower()


class LoginRedirectViewTestCase(BaseTestCase):
    def test_login_redirect_for_authenticated_user(self) -> None:
        response = self.client.get(reverse('django_spire:auth:redirect:login'))
        assert response.status_code == 302

    def test_login_redirect_for_unauthenticated_user(self) -> None:
        self.client.logout()
        response = self.client.get(reverse('django_spire:auth:redirect:login'))
        assert response.status_code == 302
