from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from django_spire.auth.sms.choices import AuthSmsCodePurposeChoices
from django_spire.auth.sms.decorators import auth_sms_required
from django_spire.auth.sms.models import AuthSms
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def _ok_view(request: WSGIRequest) -> HttpResponse:
    return HttpResponse('OK')


class AuthSmsRequiredTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        cache.clear()

        self.factory = RequestFactory()
        self.phone_number = AuthSms.objects.create(
            user=self.super_user,
            phone_number='+15551234567',
            is_verified=True,
        )

    def _decorated(self) -> HttpResponse:
        return auth_sms_required()(_ok_view)(self._request('hello'))

    def _request(self, body: str, from_number: str = '+15551234567') -> WSGIRequest:
        return self.factory.post('/', data={'From': from_number, 'Body': body})

    def test_active_session_calls_view(self) -> None:
        self.phone_number.services.processor.open_session()

        response = self._decorated()

        assert response.status_code == 200
        assert response.content == b'OK'

    def test_active_session_touches_activity(self) -> None:
        self.phone_number.services.processor.open_session()

        self._decorated()

        self.phone_number.refresh_from_db()
        assert self.phone_number.session_last_activity_datetime is not None

    def test_valid_unlock_code_opens_session_and_calls_view(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)

        response = auth_sms_required()(_ok_view)(self._request(code))

        assert response.status_code == 200
        self.phone_number.refresh_from_db()
        assert self.phone_number.session_is_active

    def test_wrong_code_returns_forbidden(self) -> None:
        code = self.phone_number.services.processor.issue_code(AuthSmsCodePurposeChoices.SESSION)
        wrong_code = '000000' if code != '000000' else '111111'

        response = auth_sms_required()(_ok_view)(self._request(wrong_code))

        assert response.status_code == 403
        self.phone_number.refresh_from_db()
        assert not self.phone_number.session_is_active
        assert self.phone_number.code_attempt_count == 1

    def test_unverified_number_returns_forbidden(self) -> None:
        AuthSms.objects.create(
            user=self.super_user,
            phone_number='+15558888888',
            is_verified=False,
        )

        response = auth_sms_required()(_ok_view)(self._request('hello', '+15558888888'))

        assert response.status_code == 403

    def test_unregistered_number_returns_forbidden(self) -> None:
        response = auth_sms_required()(_ok_view)(self._request('hello', '+15559999999'))

        assert response.status_code == 403

    def test_short_phone_number_returns_forbidden(self) -> None:
        response = auth_sms_required()(_ok_view)(self._request('hello', '1234'))

        assert response.status_code == 403

    def test_on_reject_receives_reason(self) -> None:
        rejected: list[str] = []

        def on_reject(request, sms_auth, reason) -> HttpResponse:
            rejected.append(reason)
            return HttpResponse('REJECT')

        decorated = auth_sms_required(on_reject=on_reject)(_ok_view)
        response = decorated(self._request('hello', '1234'))

        assert response.content == b'REJECT'
        assert rejected == ['invalid_phone']

    def test_request_sms_auth_is_set_on_active_session(self) -> None:
        self.phone_number.services.processor.open_session()

        captured: list[AuthSms] = []

        def capturing_view(request: WSGIRequest) -> HttpResponse:
            captured.append(request.sms_auth)
            return HttpResponse('OK')

        auth_sms_required()(capturing_view)(self._request('hello'))

        assert captured == [self.phone_number]

    @override_settings(DJANGO_SPIRE_AUTH_SMS_THROTTLE_RATE_PER_MINUTE=1)
    def test_throttled_number_returns_forbidden(self) -> None:
        self.phone_number.services.processor.open_session()

        auth_sms_required()(_ok_view)(self._request('first'))
        response = auth_sms_required()(_ok_view)(self._request('second'))

        assert response.status_code == 403
