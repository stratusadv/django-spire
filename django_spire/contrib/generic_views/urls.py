from __future__ import annotations

import re

from django.urls import get_resolver, reverse


def get_url_parameters(url: str) -> list[str]:
    """
    It extract parameter name(s) from a Django URL pattern.

    Args:
        url: URL pattern name (e.g., 'app:view_name' or 'view_name')

    Returns:
        A list of parameter name(s) found in the URL pattern

    """

    resolver = get_resolver()

    def _find(patterns: list[str], name: str):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                result = _find(pattern.url_patterns, name)

                if result:
                    return result

            if hasattr(pattern, 'name') and pattern.name == name:
                route = str(pattern.pattern)
                return re.findall(r'<\w+:(\w+)>', route)

        return []

    return _find(resolver.url_patterns, url.split(':')[-1])


def spire_reverse(url: str) -> str:
    """
    Generate URL with parameter placeholders for JavaScript template strings.

    It is similar to Django's reverse() but replaces dynamic segments with {param_name}
    placeholders that can be filled in by JavaScript. It also handles URLs with any number
    of parameters or no parameters.

    Args:
        url: URL pattern name (e.g., 'app:view_name')

    Returns:
        URL string with {param_name} placeholders for dynamic segments

    """

    parameters = get_url_parameters(url)

    if not parameters:
        return reverse(url)

    kwargs = dict.fromkeys(parameters, 0)
    url = reverse(url, kwargs=kwargs)

    for parameter in parameters:
        url = url.replace('/0/', f'/{{{parameter}}}/', 1)

    return url
