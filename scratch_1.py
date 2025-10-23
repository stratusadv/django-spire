
import re
from bs4 import BeautifulSoup

import marko
from django.core.wsgi import get_wsgi_application
from markitdown.converters import HtmlConverter

get_wsgi_application()

from django_spire.knowledge.entry.version.converters.markdown_converter import \
    MarkdownConverter
from django_spire.knowledge.entry.version.models import EntryVersion

test_markdown_file = ''

test_markdown = HtmlConverter().convert_string('<i><b>testtt</b></i>')

test_html = marko.convert(test_markdown.markdown)

soup = BeautifulSoup(test_html, 'html.parser')

soup_el = soup.find().decode_contents()

with open('test.md', 'r') as f:
    markdown_content = f.read()



parsed_document = marko.parse(markdown_content)

for child in parsed_document.children:
    html_text = marko.render(child)

blocks = MarkdownConverter(EntryVersion()).convert_markdown_to_blocks(markdown_content)