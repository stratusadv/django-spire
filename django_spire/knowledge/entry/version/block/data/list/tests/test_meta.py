from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.data.list.choices import OrderedListCounterType
from django_spire.knowledge.entry.version.block.data.list.meta import (
    ChecklistItemMeta,
    OrderedListItemMeta,
)


class ChecklistItemMetaTests(BaseTestCase):
    def test_default_unchecked(self):
        meta = ChecklistItemMeta()
        assert meta.checked is False

    def test_checked_true(self):
        meta = ChecklistItemMeta(checked=True)
        assert meta.checked is True

    def test_checked_false(self):
        meta = ChecklistItemMeta(checked=False)
        assert meta.checked is False


class OrderedListItemMetaTests(BaseTestCase):
    def test_default_values(self):
        meta = OrderedListItemMeta()
        assert meta.start is None
        assert meta.counterType is None

    def test_with_start(self):
        meta = OrderedListItemMeta(start=5)
        assert meta.start == 5

    def test_with_counter_type_numeric(self):
        meta = OrderedListItemMeta(counterType=OrderedListCounterType.NUMERIC)
        assert meta.counterType == OrderedListCounterType.NUMERIC

    def test_with_counter_type_upper_roman(self):
        meta = OrderedListItemMeta(counterType=OrderedListCounterType.UPPER_ROMAN)
        assert meta.counterType == OrderedListCounterType.UPPER_ROMAN

    def test_with_counter_type_lower_roman(self):
        meta = OrderedListItemMeta(counterType=OrderedListCounterType.LOWER_ROMAN)
        assert meta.counterType == OrderedListCounterType.LOWER_ROMAN

    def test_with_counter_type_upper_alpha(self):
        meta = OrderedListItemMeta(counterType=OrderedListCounterType.UPPER_ALPHA)
        assert meta.counterType == OrderedListCounterType.UPPER_ALPHA

    def test_with_counter_type_lower_alpha(self):
        meta = OrderedListItemMeta(counterType=OrderedListCounterType.LOWER_ALPHA)
        assert meta.counterType == OrderedListCounterType.LOWER_ALPHA

    def test_with_all_values(self):
        meta = OrderedListItemMeta(start=10, counterType=OrderedListCounterType.NUMERIC)
        assert meta.start == 10
        assert meta.counterType == OrderedListCounterType.NUMERIC
