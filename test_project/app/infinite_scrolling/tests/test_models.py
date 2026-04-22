from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase


class InfiniteScrollingModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
