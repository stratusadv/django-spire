from __future__ import annotations

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.mfa.utils import get_or_generate_user_mfa_code
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class GetOrGenerateUserMfaCodeTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_generates_new_code_when_none_exists(self) -> None:
        mfa_code = get_or_generate_user_mfa_code(self.user)
        assert mfa_code is not None
        assert mfa_code.user == self.user
        assert mfa_code.is_valid() is True

    def test_returns_existing_valid_code(self) -> None:
        existing_code = MfaCode.generate_code(self.user)
        result = get_or_generate_user_mfa_code(self.user)
        assert result.pk == existing_code.pk

    def test_generates_new_code_when_existing_expired(self) -> None:
        existing_code = MfaCode.generate_code(self.user)
        existing_code.set_expired()

        new_code = get_or_generate_user_mfa_code(self.user)
        assert new_code.pk != existing_code.pk
        assert new_code.is_valid() is True

    def test_returns_same_code_on_multiple_calls(self) -> None:
        code1 = get_or_generate_user_mfa_code(self.user)
        code2 = get_or_generate_user_mfa_code(self.user)
        assert code1.pk == code2.pk

    def test_different_users_get_different_codes(self) -> None:
        user2 = create_user(username='testuser2')
        code1 = get_or_generate_user_mfa_code(self.user)
        code2 = get_or_generate_user_mfa_code(user2)
        assert code1.pk != code2.pk
        assert code1.user != code2.user

    def test_generated_code_is_persisted(self) -> None:
        mfa_code = get_or_generate_user_mfa_code(self.user)
        assert MfaCode.objects.filter(pk=mfa_code.pk).exists() is True

    def test_generates_valid_code_after_expiration(self) -> None:
        code1 = get_or_generate_user_mfa_code(self.user)
        code1.set_expired()
        code2 = get_or_generate_user_mfa_code(self.user)
        assert code2.is_valid() is True

    def test_code_belongs_to_correct_user(self) -> None:
        mfa_code = get_or_generate_user_mfa_code(self.user)
        assert mfa_code.user.pk == self.user.pk
        assert mfa_code.user.username == self.user.username
