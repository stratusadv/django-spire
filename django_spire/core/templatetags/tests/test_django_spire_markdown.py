from __future__ import annotations

import unittest
from pathlib import Path

from django.conf import settings
from django.template import Context, Template

from django_spire.core.templatetags.django_spire_markdown import (
    _render_markdown_cached,
    _render_markdown_stripped_cached,
    render_markdown,
    render_markdown_stripped,
)


class TestRenderMarkdown(unittest.TestCase):
    def setUp(self) -> None:
        self.test_docs_dir = Path(settings.BASE_DIR) / 'test_project' / 'docs'
        self.test_file = self.test_docs_dir / 'sample_readme.md'
        self.test_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_file.write_text('# Hello\n\nThis is **bold** text.')

    def tearDown(self) -> None:
        _render_markdown_cached.cache_clear()
        _render_markdown_stripped_cached.cache_clear()
        if self.test_file.exists():
            self.test_file.unlink()

    def test_render_markdown_file_found(self) -> None:
        result = render_markdown('test_project/docs/sample_readme.md')
        assert result is not None
        assert '<h1>Hello</h1>' in result
        assert '<strong>bold</strong>' in result

    def test_render_markdown_file_not_found(self) -> None:
        result = render_markdown('nonexistent/file.md')
        assert result is None

    def test_render_markdown_cached(self) -> None:
        path = 'test_project/docs/sample_readme.md'
        result1 = render_markdown(path)
        result2 = render_markdown(path)
        assert result1 == result2
        assert _render_markdown_cached.cache_info().hits == 1


class TestRenderMarkdownStripped(unittest.TestCase):
    def setUp(self) -> None:
        self.test_docs_dir = Path(settings.BASE_DIR) / 'test_project' / 'docs'
        self.test_file = self.test_docs_dir / 'sample_readme.md'
        self.test_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_file.write_text('# Hello\n\nThis is **bold** text.')

    def tearDown(self) -> None:
        _render_markdown_cached.cache_clear()
        _render_markdown_stripped_cached.cache_clear()
        if self.test_file.exists():
            self.test_file.unlink()

    def test_render_markdown_stripped_file_found(self) -> None:
        result = render_markdown_stripped('test_project/docs/sample_readme.md')
        assert result is not None
        assert 'Hello' in result
        assert 'bold' in result
        assert '<h1>' not in result
        assert '<strong>' not in result

    def test_render_markdown_stripped_file_not_found(self) -> None:
        result = render_markdown_stripped('nonexistent/file.md')
        assert result is None

    def test_render_markdown_stripped_cached(self) -> None:
        path = 'test_project/docs/sample_readme.md'
        result1 = render_markdown_stripped(path)
        result2 = render_markdown_stripped(path)
        assert result1 == result2
        assert _render_markdown_stripped_cached.cache_info().hits == 1


class TestRenderMarkdownTemplateRendering(unittest.TestCase):
    def setUp(self) -> None:
        self.test_docs_dir = Path(settings.BASE_DIR) / 'test_project' / 'docs'
        self.test_file = self.test_docs_dir / 'sample_readme.md'
        self.test_file.parent.mkdir(parents=True, exist_ok=True)
        self.test_file.write_text('# Test\n\nThis is **test** content.')

    def tearDown(self) -> None:
        _render_markdown_cached.cache_clear()
        _render_markdown_stripped_cached.cache_clear()
        if self.test_file.exists():
            self.test_file.unlink()

    def test_render_markdown_template_tag(self) -> None:
        template_code = """
            {% load django_spire_markdown %}
            {% render_markdown "test_project/docs/sample_readme.md" %}
        """
        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert '<h1>Test</h1>' in rendered
        assert '<strong>test</strong>' in rendered

    def test_render_markdown_as_context_variable(self) -> None:
        template_code = """
            {% load django_spire_markdown %}
            {% render_markdown "test_project/docs/sample_readme.md" as md %}
            {% if md %}
                <div class="alert alert-success">{{ md }}</div>
            {% else %}
                <div class="alert alert-warning">Not found</div>
            {% endif %}
        """
        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert '<div class="alert alert-success">' in rendered
        assert '<h1>Test</h1>' in rendered

    def test_render_markdown_not_found_as_context_variable(self) -> None:
        template_code = """
            {% load django_spire_markdown %}
            {% render_markdown "nonexistent/file.md" as md %}
            {% if md %}
                <div>{{ md }}</div>
            {% else %}
                <div class="alert alert-warning">File not found</div>
            {% endif %}
        """
        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert '<div class="alert alert-warning">File not found</div>' in rendered

    def test_render_markdown_stripped_template_tag(self) -> None:
        template_code = """
            {% load django_spire_markdown %}
            {% render_markdown_stripped "test_project/docs/sample_readme.md" %}
        """
        tmpl = Template(template_code)
        rendered = tmpl.render(Context())
        assert 'Test' in rendered
        assert 'test' in rendered
        assert '<h1>' not in rendered
        assert '<strong>' not in rendered
