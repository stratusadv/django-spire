from __future__ import annotations

import json
import string

import unittest

from unittest.mock import MagicMock

from django_spire.core.templatetags.django_spire_message import django_messages_to_json


class TestDjangoMessagesToJson(unittest.TestCase):
    def test_empty_messages(self) -> None:
        result = django_messages_to_json([])
        assert json.loads(result) == []

    def test_multiple_messages(self) -> None:
        messages = [
            MagicMock(message='First', level_tag='info'),
            MagicMock(message='Second', level_tag='error'),
        ]

        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert len(parsed) == 2
        assert parsed[0]['message'] == 'First'
        assert parsed[0]['type'] == 'info'
        assert parsed[1]['message'] == 'Second'
        assert parsed[1]['type'] == 'error'

    def test_single_message(self) -> None:
        messages = [MagicMock(message='Test message', level_tag='success')]

        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert parsed[0]['message'] == 'Test message'
        assert parsed[0]['type'] == 'success'
        assert len(parsed[0]['id']) == 8

    def test_message_id_is_ascii_only(self) -> None:
        messages = [MagicMock(message='Test', level_tag='info')]

        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert all(ch in string.ascii_letters for ch in parsed[0]['id'])

    def test_different_level_tags(self) -> None:
        test_cases = [
            ('warning', 'warning'),
            ('error', 'error'),
            ('debug', 'debug'),
            ('info', 'info'),
        ]

        messages = [MagicMock(message=msg, level_tag=tag) for msg, tag in test_cases]
        result = django_messages_to_json(messages)
        parsed = json.loads(result)

        assert len(parsed) == 4
        for i, (expected_msg, expected_tag) in enumerate(test_cases):
            assert parsed[i]['message'] == expected_msg
            assert parsed[i]['type'] == expected_tag
