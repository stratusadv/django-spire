from __future__ import annotations

import pytest
from django.test import TestCase

from django_spire.constants import __VERSION__, MAINTENANCE_MODE_SETTINGS_KEY


class TestConsts(TestCase):
    def test_maintenance_mode_settings_name(self) -> None:
        assert MAINTENANCE_MODE_SETTINGS_KEY == 'MAINTENANCE_MODE'

    def test_version_is_string(self) -> None:
        assert isinstance(__VERSION__, str)

    def test_version_format(self) -> None:
        parts = __VERSION__.split('.')

        assert len(parts) == 3

        for part in parts:
            if not part.isdigit() and 'a' not in str(part):
                pytest.fail('Version must be an integer or contain the `a` character')
