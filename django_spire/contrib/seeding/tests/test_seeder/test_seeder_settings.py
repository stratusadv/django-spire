import importlib

import pytest

from django_spire.contrib.seeding import settings


class TestSeedingSettings:
    def test_seeding_multiplier_defaults_to_one_when_env_unset(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv('SEEDING_MULTIPLIER', raising=False)
        importlib.reload(settings)
        assert settings.SEEDING_MULTIPLIER == 1.0

    def test_seeding_multiplier_reads_from_env(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv('SEEDING_MULTIPLIER', '2.5')
        importlib.reload(settings)
        assert settings.SEEDING_MULTIPLIER == 2.5
