from __future__ import annotations

import json
import unittest

from django_spire.core.templatetags.django_spire_json import to_json


class TestToJson(unittest.TestCase):
    def test_dict(self) -> None:
        result = to_json({'key': 'value'})
        assert result == '{"key": "value"}'

    def test_invalid_value(self) -> None:
        result = to_json(object())
        assert result == ''

    def test_list(self) -> None:
        result = to_json([1, 2, 3])
        assert result == '[1, 2, 3]'

    def test_nested_structure(self) -> None:
        result = to_json({'list': [1, 2, 3], 'nested': {'key': 'value'}})
        parsed = json.loads(result)

        assert parsed['list'] == [1, 2, 3]
        assert parsed['nested'] == {'key': 'value'}

    def test_string(self) -> None:
        result = to_json('hello')
        assert result == '"hello"'

    def test_none_value(self) -> None:
        result = to_json(None)
        assert result == 'null'

    def test_boolean_values(self) -> None:
        result = to_json({'active': True, 'deleted': False})
        parsed = json.loads(result)
        assert parsed['active'] is True
        assert parsed['deleted'] is False
