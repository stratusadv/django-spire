"""Middleware for auto-loading Lit web components with code splitting."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import TYPE_CHECKING, Callable

from django.conf import settings
from django.templatetags.static import static

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class CustomElementParser(HTMLParser):
    """HTML parser that extracts custom element tag names."""

    def __init__(self) -> None:
        super().__init__()
        self.custom_elements: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if '-' in tag:
            self.custom_elements.add(tag)


def get_components_base_path() -> str:
    """Get the base static path for Lit components."""
    return getattr(settings, 'LIT_COMPONENTS_PATH', 'lit/components')


def tag_to_class_name(tag: str) -> str:
    """Convert a tag name to a PascalCase class name (e.g., 'task-item' -> 'TaskItem')."""
    return ''.join(word.capitalize() for word in tag.split('-'))


class LitComponentsMiddleware:
    """
    Middleware that scans HTML responses for custom element tags and
    auto-injects ES module script imports for each component found.

    Custom elements are identified by tags containing a hyphen (per web components spec).
    For each unique custom element found, a script tag is injected before </body>.

    Component files should:
    1. Be placed in the static directory at LIT_COMPONENTS_PATH (default: 'lit/components/')
    2. Be named to match the tag name (e.g., 'task-item.js' for <task-item>)
    3. Export a default class extending SpireElement

    The middleware auto-registers each component with customElements.define().

    Configuration in settings.py:
        MIDDLEWARE = [
            ...
            'django_spire.lit.middleware.LitComponentsMiddleware',
        ]

        # Optional: customize the components path
        LIT_COMPONENTS_PATH = 'myapp/components'
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Only process HTML responses
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type:
            return response

        # Only process successful responses with content
        if response.status_code != 200 or not hasattr(response, 'content'):
            return response

        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            return response

        # Parse HTML and find custom elements
        parser = CustomElementParser()
        parser.feed(content)
        component_names = sorted(parser.custom_elements)

        if not component_names:
            return response

        # Generate imports and registration calls
        base_path = get_components_base_path()
        imports = []
        registrations = []

        for name in component_names:
            component_url = static(f'{base_path}/{name}.js')
            class_name = tag_to_class_name(name)
            imports.append(f"import {class_name} from '{component_url}';")
            registrations.append(f"customElements.define('{name}', {class_name});")

        script_content = '\n'.join(imports) + '\n\n' + '\n'.join(registrations)
        scripts_html = f'<script type="module">\n{script_content}\n</script>'

        # Inject before </body>
        if '</body>' in content:
            content = content.replace('</body>', f'{scripts_html}\n</body>')
            response.content = content.encode('utf-8')
            response['Content-Length'] = len(response.content)

        return response
