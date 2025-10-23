
import re

import bs4
from bs4 import BeautifulSoup

import marko
from django.core.wsgi import get_wsgi_application
from markitdown.converters import HtmlConverter
from marko.block import List
from marko.md_renderer import MarkdownRenderer

get_wsgi_application()

from django_spire.knowledge.entry.version.converters.markdown_converter import \
    MarkdownConverter
from django_spire.knowledge.entry.version.models import EntryVersion

with open('test.md', 'r') as f:
    markdown_content = f.read()

parsed_document = marko.parse(markdown_content)

for child in parsed_document.children:
    if isinstance(child, List):
        rendered = marko.render(child.children[0])
        print(rendered)

blocks = MarkdownConverter(EntryVersion()).convert_markdown_to_blocks(markdown_content)