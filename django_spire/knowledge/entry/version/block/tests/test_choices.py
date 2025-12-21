from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.data.list.choices import (
    ListEditorBlockDataStyle,
    OrderedListCounterType,
)


class BlockTypeChoicesTests(BaseTestCase):
    def test_text_value(self):
        assert BlockTypeChoices.TEXT == 'text'

    def test_heading_value(self):
        assert BlockTypeChoices.HEADING == 'heading'

    def test_list_value(self):
        assert BlockTypeChoices.LIST == 'list'

    def test_choices_count(self):
        assert len(BlockTypeChoices.choices) == 3


class ListEditorBlockDataStyleTests(BaseTestCase):
    def test_unordered_value(self):
        assert ListEditorBlockDataStyle.UNORDERED == 'unordered'

    def test_ordered_value(self):
        assert ListEditorBlockDataStyle.ORDERED == 'ordered'

    def test_checklist_value(self):
        assert ListEditorBlockDataStyle.CHECKLIST == 'checklist'

    def test_choices_count(self):
        assert len(ListEditorBlockDataStyle.choices) == 3


class OrderedListCounterTypeTests(BaseTestCase):
    def test_numeric_value(self):
        assert OrderedListCounterType.NUMERIC == 'numeric'

    def test_upper_roman_value(self):
        assert OrderedListCounterType.UPPER_ROMAN == 'upper-roman'

    def test_lower_roman_value(self):
        assert OrderedListCounterType.LOWER_ROMAN == 'lower-roman'

    def test_upper_alpha_value(self):
        assert OrderedListCounterType.UPPER_ALPHA == 'upper-alpha'

    def test_lower_alpha_value(self):
        assert OrderedListCounterType.LOWER_ALPHA == 'lower-alpha'

    def test_choices_count(self):
        assert len(OrderedListCounterType.choices) == 5
