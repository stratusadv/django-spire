from __future__ import annotations

from django.contrib.auth import get_user
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

    def test_login_with_whitespace_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': '   ', 'password': 'testpassword123'}
        )
        assert response.status_code == 200

    def test_login_case_sensitive_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'TESTUSER', 'password': 'testpassword123'}
        )
        assert response.status_code == 200

    def test_login_case_sensitive_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'TESTPASSWORD123'}
        )
        assert response.status_code == 200

    def test_login_sets_session(self) -> None:
        self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'testpassword123'}
        )
        user = get_user(self.client)
        assert user.is_authenticated

    def test_login_with_sql_injection_attempt(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': "'; DROP TABLE users; --", 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_xss_attempt(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': '<script>alert("xss")</script>', 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_very_long_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'a' * 1000, 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_very_long_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'a' * 1000}
        )
        assert response.status_code == 200

    def test_login_with_unicode_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'tëstüsér', 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_unicode_password(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'pässwörd'}
        )
        assert response.status_code == 200

    def test_login_get_request_does_not_authenticate(self) -> None:
        response = self.client.get(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'testuser', 'password': 'testpassword123'}
        )
        user = get_user(self.client)
        assert not user.is_authenticated
        assert response.status_code == 200

    def test_login_with_null_bytes(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'test\x00user', 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_newline_in_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'test\nuser', 'password': 'password'}
        )
        assert response.status_code == 200

    def test_login_with_tab_in_username(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:login'),
            data={'username': 'test\tuser', 'password': 'password'}
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
        assert self.user.check_password('newpassword456')

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
        assert self.user.check_password('oldpassword123')

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

    def test_password_change_same_as_old(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'oldpassword123',
                'new_password2': 'oldpassword123'
            }
        )
        assert response.status_code in (200, 302)

    def test_password_change_with_unicode(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'nëwpässwörd456',
                'new_password2': 'nëwpässwörd456'
            }
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.check_password('nëwpässwörd456')

    def test_password_change_very_long_password(self) -> None:
        long_password = 'a' * 128
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': long_password,
                'new_password2': long_password
            }
        )
        assert response.status_code == 302

    def test_password_change_with_spaces(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'new password 456',
                'new_password2': 'new password 456'
            }
        )
        assert response.status_code == 302
        self.user.refresh_from_db()
        assert self.user.check_password('new password 456')

    def test_password_change_preserves_session(self) -> None:
        self.client.post(
            reverse('django_spire:auth:admin:password_change'),
            data={
                'old_password': 'oldpassword123',
                'new_password1': 'newpassword456',
                'new_password2': 'newpassword456'
            }
        )
        user = get_user(self.client)
        assert user.is_authenticated


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

    def test_password_reset_with_uppercase_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'TEST@EXAMPLE.COM'}
        )
        assert response.status_code == 302

    def test_password_reset_with_mixed_case_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'Test@Example.Com'}
        )
        assert response.status_code == 302

    def test_password_reset_with_whitespace_email(self) -> None:
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': '  test@example.com  '}
        )
        assert response.status_code in (200, 302)

    def test_password_reset_inactive_user(self) -> None:
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse('django_spire:auth:admin:password_reset'),
            data={'email': 'test@example.com'}
        )
        assert response.status_code == 302


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

    def test_logout_clears_session(self) -> None:
        self.client.get(reverse('django_spire:auth:redirect:logout'))
        user = get_user(self.client)
        assert not user.is_authenticated


class LoginRedirectViewTestCase(BaseTestCase):
    def test_login_redirect_for_authenticated_user(self) -> None:
        response = self.client.get(reverse('django_spire:auth:redirect:login'))
        assert response.status_code == 302

    def test_login_redirect_for_unauthenticated_user(self) -> None:
        self.client.logout()
        response = self.client.get(reverse('django_spire:auth:redirect:login'))
        assert response.status_code == 302
