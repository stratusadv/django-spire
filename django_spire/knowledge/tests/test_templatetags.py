from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.templatetags.spire_knowledge_tags import format_to_html


class SpireKnowledgeTagsTests(BaseTestCase):
    def test_format_to_html_empty_string(self):
        result = format_to_html('')
        assert result == '&nbsp;'

    def test_format_to_html_none(self):
        result = format_to_html(None)
        assert result == '&nbsp;'

    def test_format_to_html_line_breaks(self):
        result = format_to_html('Line1\nLine2')
        assert '<br>' in result

    def test_format_to_html_bold(self):
        result = format_to_html('**bold text**')
        assert '<span class="fw-bold">bold text</span>' in result

    def test_format_to_html_italic(self):
        result = format_to_html('*italic text*')
        assert '<span class="fst-italic">italic text</span>' in result

    def test_format_to_html_strikethrough(self):
        result = format_to_html('~~strikethrough~~')
        assert '<span class="text-decoration-line-through">strikethrough</span>' in result

    def test_format_to_html_mixed(self):
        result = format_to_html('**bold** and *italic* and ~~strike~~')
        assert '<span class="fw-bold">bold</span>' in result
        assert '<span class="fst-italic">italic</span>' in result
        assert '<span class="text-decoration-line-through">strike</span>' in result

    def test_format_to_html_plain_text(self):
        result = format_to_html('plain text')
        assert result == 'plain text'
