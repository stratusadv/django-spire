from __future__ import annotations

from dateutil import relativedelta
from django.utils.timezone import localtime

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class MfaCodeModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_generate_code_creates_valid_code(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        code_value = int(mfa_code.code)
        assert mfa_code.user == self.user
        assert 0 <= code_value <= 999999

    def test_generate_code_sets_expiration(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code.expiration_datetime > localtime()

    def test_generate_code_expiration_is_five_minutes(self) -> None:
        before = localtime()
        mfa_code = MfaCode.generate_code(self.user)
        after = localtime()
        expected_min = before + relativedelta.relativedelta(minutes=5)
        expected_max = after + relativedelta.relativedelta(minutes=5, seconds=1)
        assert mfa_code.expiration_datetime >= expected_min
        assert mfa_code.expiration_datetime <= expected_max

    def test_is_valid_returns_true_for_unexpired(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code.is_valid()

    def test_is_valid_returns_false_for_expired(self) -> None:
        mfa_code = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime=localtime() - relativedelta.relativedelta(minutes=1)
        )
        assert not mfa_code.is_valid()

    def test_is_valid_boundary_expired(self) -> None:
        mfa_code = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime=localtime() - relativedelta.relativedelta(seconds=1)
        )
        assert not mfa_code.is_valid()

    def test_set_expired(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code.is_valid()
        mfa_code.set_expired()
        assert not mfa_code.is_valid()

    def test_set_expired_persists(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        mfa_code.set_expired()
        mfa_code.refresh_from_db()
        assert not mfa_code.is_valid()

    def test_str_representation(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        expected = f'{mfa_code.expiration_datetime} - {mfa_code.code}'
        assert str(mfa_code) == expected

    def test_code_is_valid_numeric(self) -> None:
        for _ in range(10):
            mfa_code = MfaCode.generate_code(self.user)
            code_value = int(mfa_code.code)
            assert 0 <= code_value <= 999999
            mfa_code.delete()

    def test_multiple_codes_for_same_user(self) -> None:
        code1 = MfaCode.generate_code(self.user)
        code1.set_expired()
        code2 = MfaCode.generate_code(self.user)
        assert code1.pk != code2.pk

    def test_codes_for_different_users(self) -> None:
        user2 = create_user(username='testuser2')
        code1 = MfaCode.generate_code(self.user)
        code2 = MfaCode.generate_code(user2)
        assert code1.user != code2.user

    def test_code_user_relationship(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code.user.pk == self.user.pk

    def test_code_deletion_with_user(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        code_pk = mfa_code.pk
        self.user.delete()
        assert not MfaCode.objects.filter(pk=code_pk).exists()

    def test_meta_db_table(self) -> None:
        assert MfaCode._meta.db_table == 'django_spire_authentication_mfa_code'

    def test_meta_verbose_name(self) -> None:
        assert MfaCode._meta.verbose_name == 'MFA Code'
        assert MfaCode._meta.verbose_name_plural == 'MFA Codes'

    def test_code_length_is_six(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert len(str(mfa_code.code)) <= 6
        assert int(mfa_code.code) <= 999999

    def test_code_is_string(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert isinstance(mfa_code.code, (str, int))

    def test_code_field_max_length(self) -> None:
        max_length = MfaCode._meta.get_field('code').max_length
        assert max_length == 6

    def test_code_field_is_unique(self) -> None:
        assert MfaCode._meta.get_field('code').unique

    def test_code_field_is_not_editable(self) -> None:
        assert not MfaCode._meta.get_field('code').editable

    def test_expiration_field_is_not_editable(self) -> None:
        assert not MfaCode._meta.get_field('expiration_datetime').editable

    def test_user_foreign_key(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code.user_id == self.user.pk

    def test_user_related_name(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        assert mfa_code in self.user.mfa_codes.all()

    def test_generate_code_creates_unique_codes(self) -> None:
        codes = set()
        for _ in range(100):
            mfa_code = MfaCode.generate_code(self.user)
            codes.add(mfa_code.code)
            mfa_code.delete()
        assert len(codes) > 90

    def test_is_valid_exact_expiration_time(self) -> None:
        mfa_code = MfaCode.objects.create(
            user=self.user,
            code='654321',
            expiration_datetime=localtime()
        )
        assert not mfa_code.is_valid()

    def test_code_with_leading_zeros(self) -> None:
        mfa_code = MfaCode.objects.create(
            user=self.user,
            code='000123',
            expiration_datetime=localtime() + relativedelta.relativedelta(minutes=5)
        )
        assert mfa_code.code == '000123'
        assert len(mfa_code.code) == 6


class MfaCodeQuerySetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_valid_code_returns_unexpired(self) -> None:
        mfa_code = MfaCode.generate_code(self.user)
        result = MfaCode.objects.valid_code(self.user)
        assert result == mfa_code

    def test_valid_code_returns_none_for_expired(self) -> None:
        MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime=localtime() - relativedelta.relativedelta(minutes=1)
        )
        result = MfaCode.objects.valid_code(self.user)
        assert result is None

    def test_valid_code_returns_none_for_different_user(self) -> None:
        other_user = create_user(username='otheruser')
        MfaCode.generate_code(other_user)
        result = MfaCode.objects.valid_code(self.user)
        assert result is None

    def test_valid_code_returns_none_when_no_codes(self) -> None:
        result = MfaCode.objects.valid_code(self.user)
        assert result is None

    def test_valid_code_returns_first_valid(self) -> None:
        MfaCode.objects.create(
            user=self.user,
            code='111111',
            expiration_datetime=localtime() - relativedelta.relativedelta(minutes=1)
        )
        valid_code = MfaCode.generate_code(self.user)
        result = MfaCode.objects.valid_code(self.user)
        assert result == valid_code

    def test_valid_code_with_multiple_users(self) -> None:
        user2 = create_user(username='testuser2')
        code1 = MfaCode.generate_code(self.user)
        MfaCode.generate_code(user2)
        result = MfaCode.objects.valid_code(self.user)
        assert result == code1

    def test_valid_code_ignores_other_users_codes(self) -> None:
        user2 = create_user(username='testuser2')
        MfaCode.generate_code(user2)
        result = MfaCode.objects.valid_code(self.user)
        assert result is None

    def test_valid_code_after_expiring_previous(self) -> None:
        code1 = MfaCode.generate_code(self.user)
        code1.set_expired()
        code2 = MfaCode.generate_code(self.user)
        result = MfaCode.objects.valid_code(self.user)
        assert result == code2

    def test_valid_code_multiple_valid_returns_first(self) -> None:
        code1 = MfaCode.generate_code(self.user)
        MfaCode.objects.create(
            user=self.user,
            code='999999',
            expiration_datetime=localtime() + relativedelta.relativedelta(minutes=10)
        )
        result = MfaCode.objects.valid_code(self.user)
        assert result == code1
