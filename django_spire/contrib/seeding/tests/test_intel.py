from __future__ import annotations

from django.test import TestCase

from django_spire.contrib.seeding.intelligence.intel import SeedingIntel, SourceIntel


class TestSeedingIntel(TestCase):
    def test_is_iterable(self) -> None:
        intel = SeedingIntel(items=[{'name': 'test1'}, {'name': 'test2'}])

        result = list(intel)

        assert result == [{'name': 'test1'}, {'name': 'test2'}]

    def test_items_attribute(self) -> None:
        items = [{'name': 'test'}]
        intel = SeedingIntel(items=items)

        assert intel.items == items


class TestSourceIntel(TestCase):
    def test_file_name_attribute(self) -> None:
        intel = SourceIntel(file_name='test.py', python_source_code='print("hello")')

        assert intel.file_name == 'test.py'

    def test_python_source_code_attribute(self) -> None:
        intel = SourceIntel(file_name='test.py', python_source_code='print("hello")')

        assert intel.python_source_code == 'print("hello")'
