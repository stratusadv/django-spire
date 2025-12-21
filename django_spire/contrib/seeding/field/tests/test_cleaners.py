from __future__ import annotations

from copy import copy

from django.test import TestCase

from django_spire.contrib.seeding.field.cleaners import normalize_seeder_fields


FIELDS = {
    'faker_tuple': ('faker', 'name'),
    'llm_type': 'llm',
    'faker_type': 'faker',
    'static_type': 'static',
    'callable_type': 'callable',
    'custom_type': 'custom',
    'static_bool': True,
    'static_str': 'approved',
    'static_int': 10,
    'callable_func': lambda: 'now',
    'exclude_str': 'exclude',
    'exclude_tuple': ('exclude',)
}


class TestNormalizeSeederFields(TestCase):
    def test_excludes_fields(self) -> None:
        fields = copy(FIELDS)

        normalized = normalize_seeder_fields(fields)

        assert 'exclude_str' not in normalized
        assert 'exclude_tuple' not in normalized
        assert 'static_str' in normalized

    def test_normalizes_callable(self) -> None:
        fields = {'callable_func': FIELDS['callable_func']}

        normalized = normalize_seeder_fields(fields)

        assert normalized['callable_func'][0] == 'callable'
        assert callable(normalized['callable_func'][1])

    def test_normalizes_faker_tuple(self) -> None:
        fields = {'faker_tuple': FIELDS['faker_tuple']}

        normalized = normalize_seeder_fields(fields)

        assert normalized['faker_tuple'] == ('faker', 'name')

    def test_normalizes_single_value_strings_to_tuples(self) -> None:
        fields = {
            k: FIELDS[k] for k in (
                'llm_type', 'faker_type', 'static_type', 'callable_type', 'custom_type'
            )
        }

        normalized = normalize_seeder_fields(fields)

        for key, value in fields.items():
            assert normalized[key] == (value,)

    def test_normalizes_static_values(self) -> None:
        fields = {
            'static_bool': FIELDS['static_bool'],
            'static_str': FIELDS['static_str'],
            'static_int': FIELDS['static_int']
        }

        normalized = normalize_seeder_fields(fields)

        assert normalized['static_bool'] == ('static', True)
        assert normalized['static_str'] == ('static', 'approved')
        assert normalized['static_int'] == ('static', 10)
