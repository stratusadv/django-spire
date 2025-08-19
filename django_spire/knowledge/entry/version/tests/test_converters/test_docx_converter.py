from unittest.mock import patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


class DocxConverterTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_entry_version = create_test_entry_version()

    @patch('django_spire.knowledge.entry.version.converters.docx_converter.markdown_format_bot.process')
    def test_improve_markdown_structure(self):
