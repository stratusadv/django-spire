from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING

from django import template
from django.urls import get_resolver

if TYPE_CHECKING:
    from django.urls.resolvers import URLResolver

register = template.Library()


def _extract_patterns(
    resolver: URLResolver,
    namespace: str = '',
    prefix: str = '',
) -> dict[str, str]:
    """
    Recursively extract URL patterns from the resolver.
    Converts Django URL patterns to JS template strings.
    e.g., /task/<int:pk>/detail/ -> /task/${pk}/detail/

    Args:
        resolver: The URL resolver to extract patterns from.
        namespace: The current namespace prefix (e.g., 'task:page').
        prefix: The current URL path prefix (e.g., 'task/page/').
    """
    patterns: dict[str, str] = {}

    for pattern in resolver.url_patterns:
        # Get the route segment for this pattern
        route_segment = str(pattern.pattern)

        if hasattr(pattern, 'url_patterns'):
            # Nested namespace (included URLconf)
            ns = f"{namespace}:{pattern.namespace}" if namespace else pattern.namespace
            new_prefix = prefix + route_segment
            patterns.update(_extract_patterns(pattern, ns, new_prefix))
        elif hasattr(pattern, 'name') and pattern.name:
            # Named URL pattern
            name = f"{namespace}:{pattern.name}" if namespace else pattern.name
            full_route = prefix + route_segment
            # Convert <type:name> or <name> to ${name}
            full_route = re.sub(r'<(\w+:)?(\w+)>', r'${\2}', full_route)
            patterns[name] = '/' + full_route

    return patterns


def _filter_patterns(
    patterns: dict[str, str],
    include: str | None = None,
    exclude: str | None = None,
) -> dict[str, str]:
    """
    Filter URL patterns by include/exclude prefixes.

    Args:
        patterns: Dictionary of URL name to pattern mappings.
        include: Optional comma-separated namespace prefixes to include.
        exclude: Optional comma-separated namespace prefixes to exclude.

    Returns:
        Filtered dictionary of URL patterns.
    """
    if include:
        prefixes = [p.strip() for p in include.split(',')]
        patterns = {
            k: v for k, v in patterns.items()
            if any(k.startswith(p) for p in prefixes)
        }

    if exclude:
        prefixes = [p.strip() for p in exclude.split(',')]
        patterns = {
            k: v for k, v in patterns.items()
            if not any(k.startswith(p) for p in prefixes)
        }

    return patterns


@register.simple_tag
def js_url_patterns(include: str | None = None, exclude: str | None = None) -> str:
    """
    Outputs URL patterns as a JSON object for client-side URL reversing.

    Args:
        include: Optional comma-separated namespace prefixes to include (e.g., 'task:,api:').
        exclude: Optional comma-separated namespace prefixes to exclude (e.g., 'admin:').

    Returns:
        JSON string of URL patterns.

    Usage in template:
        {% load django_spire_urls %}
        <script>
            const URL_PATTERNS = {% js_url_patterns %};
            // or with filtering:
            const URL_PATTERNS = {% js_url_patterns include='task:,api:' %};
        </script>
    """
    resolver = get_resolver()
    patterns = _extract_patterns(resolver)
    patterns = _filter_patterns(patterns, include, exclude)

    return json.dumps(patterns)


@register.inclusion_tag('django_spire/navigation/js_url_helper.html')
def js_url_helper(
    include: str | None = None,
    exclude: str | None = None,
) -> dict[str, str]:
    """
    Outputs URL patterns and the url() helper function.

    Args:
        include: Optional comma-separated namespace prefixes to include.
        exclude: Optional comma-separated namespace prefixes to exclude.

    Returns:
        Context dictionary containing the JSON-encoded URL patterns.

    Usage in template:
        {% load django_spire_urls %}
        {% js_url_helper %}

        Then in JS/Alpine:
        <a :href="url('task:page:detail', {pk: item.id})">
    """
    resolver = get_resolver()
    patterns = _extract_patterns(resolver)
    patterns = _filter_patterns(patterns, include, exclude)

    return {'patterns': json.dumps(patterns)}
