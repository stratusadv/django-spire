from __future__ import annotations

import os

import pytest

from django_spire.contrib.sync.tests.database.fuzz import parse_seed, run_fuzz


pytestmark = pytest.mark.simulation


class TestFuzzShort:
    @pytest.mark.parametrize('seed', range(20))
    def test_seed(self, seed: int) -> None:
        run_fuzz(seed, events_max=500)


class TestFuzzMedium:
    @pytest.mark.parametrize('seed', range(10))
    def test_seed(self, seed: int) -> None:
        run_fuzz(seed, events_max=5_000)


class TestFuzzLong:
    @pytest.mark.slow
    @pytest.mark.parametrize('seed', range(5))
    def test_seed(self, seed: int) -> None:
        run_fuzz(seed, events_max=50_000)


class TestFuzzCI:
    @pytest.mark.slow
    def test_commit_seed(self) -> None:
        raw = os.environ.get('CI_COMMIT_SHA', '0')
        seed = parse_seed(raw) if len(raw) == 40 else 0
        run_fuzz(seed, events_max=20_000)
