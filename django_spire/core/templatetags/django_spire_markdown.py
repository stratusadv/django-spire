from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import marko
from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def _read_markdown_file(file_path: str) -> str | None:
    full_path = Path(settings.BASE_DIR) / file_path
    if not full_path.exists():
        return None
    return marko.convert(full_path.read_text())


@lru_cache(maxsize=128)
def _render_markdown_cached(file_path: str) -> str | None:
    return _read_markdown_file(file_path)


@lru_cache(maxsize=128)
def _render_markdown_stripped_cached(file_path: str) -> str | None:
    html = _render_markdown_cached(file_path)
    if html is None:
        return None
    return BeautifulSoup(html, 'html.parser').get_text()


@register.simple_tag(takes_context=False)
def render_markdown(file_path: str) -> str | None:
    html = _read_markdown_file(file_path) if settings.DEBUG else _render_markdown_cached(file_path)
    if html is None:
        return None
    return mark_safe(html)  # noqa: S308


@register.simple_tag(takes_context=False)
def render_markdown_stripped(file_path: str) -> str | None:
    if settings.DEBUG:
        html = _read_markdown_file(file_path)
        if html is None:
            return None
        return BeautifulSoup(html, 'html.parser').get_text()
    return _render_markdown_stripped_cached(file_path)
