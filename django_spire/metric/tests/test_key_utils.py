from __future__ import annotations

import pytest
from django.test import SimpleTestCase, TestCase

from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.key_utils import (
    KEY_MAX_LENGTH,
    LOCAL_KEY_PATTERN,
    STORAGE_KEY_PATTERN,
    object_key,
    unique_key,
    validate_local_key,
)


class ObjectKeyTestCase(SimpleTestCase):
    def test_single_local_key_is_unchanged(self):
        assert object_key('store') == 'store'

    def test_joins_levels_with_object_separator(self):
        assert object_key('store', 'web') == 'store--web'
        assert object_key('store', 'orders', 'created') == 'store--orders--created'

    def test_joins_worded_segments(self):
        assert object_key('store', 'order-revenue', 'created') == 'store--order-revenue--created'


class ValidateLocalKeyTestCase(SimpleTestCase):
    def test_accepts_slugs(self):
        for key in ('store', 'order-revenue', 'a1-b2'):
            validate_local_key(key, 'statistic')

    def test_rejects_uppercase(self):
        with pytest.raises(ValueError, match='must be lowercase letters'):
            validate_local_key('Store', 'domain')

    def test_rejects_underscore(self):
        with pytest.raises(ValueError, match='must be lowercase letters'):
            validate_local_key('my_key', 'domain')

    def test_rejects_object_separator(self):
        with pytest.raises(ValueError, match='must not contain'):
            validate_local_key('sto--re', 'domain')

    def test_rejects_leading_and_trailing_hyphen(self):
        with pytest.raises(ValueError, match='must be lowercase letters'):
            validate_local_key('-a', 'domain')
        with pytest.raises(ValueError, match='must be lowercase letters'):
            validate_local_key('a-', 'domain')

    def test_rejects_empty_and_non_string(self):
        with pytest.raises(ValueError, match='must be a non-empty string'):
            validate_local_key('', 'domain')
        with pytest.raises(ValueError, match='must be a non-empty string'):
            validate_local_key(None, 'domain')

    def test_rejects_over_long_keys(self):
        with pytest.raises(ValueError, match=f'exceeds {KEY_MAX_LENGTH} characters'):
            validate_local_key('k' * (KEY_MAX_LENGTH + 1), 'domain')


class LocalKeyPatternTestCase(SimpleTestCase):
    def test_matches_slugs(self):
        for key in ('store', 'order-revenue', 'k1'):
            assert LOCAL_KEY_PATTERN.fullmatch(key)

    def test_rejects_non_slugs(self):
        for key in ('Store', 'my_key', 'sto--re', '-a', 'a-', 'a---b', ''):
            assert not LOCAL_KEY_PATTERN.fullmatch(key)


class StorageKeyPatternTestCase(SimpleTestCase):
    def test_matches_stored_keys(self):
        for key in ('store', 'order-revenue', 'store--web', 'store--orders--created'):
            assert STORAGE_KEY_PATTERN.fullmatch(key)
        assert STORAGE_KEY_PATTERN.fullmatch('store--order-revenue--created')

    def test_rejects_malformed_stored_keys(self):
        for key in ('a---b', '--a', 'a--', 'a_b', 'Store', 'a--b-', 'a--b--'):
            assert not STORAGE_KEY_PATTERN.fullmatch(key)


class UniqueKeyTestCase(SimpleTestCase):
    def test_returns_base_when_free(self):
        assert unique_key('sales', set()) == 'sales'

    def test_suffixes_collisions(self):
        assert unique_key('sales', {'sales'}) == 'sales-2'
        assert unique_key('sales', {'sales', 'sales-2'}) == 'sales-3'

    def test_suffixed_key_fits_max_length(self):
        base = 'a' * KEY_MAX_LENGTH
        key = unique_key(base, {base})
        assert len(key) == KEY_MAX_LENGTH
        assert key == base[: KEY_MAX_LENGTH - 2] + '-2'

    def test_two_digit_suffix_fits_max_length(self):
        base = 'a' * KEY_MAX_LENGTH
        taken = {base, base[: KEY_MAX_LENGTH - 2] + '-2'}
        key = unique_key(base, taken)
        assert len(key) == KEY_MAX_LENGTH
        assert key.endswith('-3')


class UniqueKeyFromNameTestCase(TestCase):
    def test_derives_slug_from_name(self):
        domain = Domain.objects.create(name='Sales', sub_domain_name='Clients')
        assert domain.key == 'sales'

    def test_underscore_in_name_becomes_word_separator(self):
        domain = Domain.objects.create(name='Sales_Web', sub_domain_name='Clients')
        assert domain.key == 'sales-web'

    def test_collision_gets_suffix(self):
        Domain.objects.create(name='Sales', sub_domain_name='Clients')
        domain = Domain.objects.create(name='Sales', sub_domain_name='Clients')
        assert domain.key == 'sales-2'

    def test_child_key_includes_parent_name(self):
        domain = Domain.objects.create(name='Sales', sub_domain_name='Clients')
        sub_domain = SubDomain.objects.create(domain=domain, name='Web')
        assert sub_domain.key == 'sales-web'

    def test_derivation_never_emits_object_separator(self):
        domain = Domain.objects.create(name='Sales', sub_domain_name='Clients')
        sub_domain = SubDomain.objects.create(domain=domain, name='A _B')
        assert sub_domain.key == 'sales-a-b'
        assert '--' not in sub_domain.key

    def test_derivation_strips_trailing_hyphen(self):
        domain = Domain.objects.create(name='A_', sub_domain_name='Clients')
        assert domain.key == 'a'
