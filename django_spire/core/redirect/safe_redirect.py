from __future__ import annotations

from typing_extensions import TYPE_CHECKING
from urllib.parse import parse_qs, unquote, urlencode, urlparse, urlunparse

from django.urls import reverse, NoReverseMatch
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def resolve_url(url: str) -> str:
    """
    Resolves a URL name into its corresponding URL path using Django's reverse function.

    :param url: The URL name or URL string to resolve.
    :return: The reversed URL if successful; otherwise, the original URL.
    """

    try:
        return reverse(url)
    except NoReverseMatch:
        return url


def is_url_valid_and_safe(url: str, allowed_hosts: set[str]) -> bool:
    """
    Determines whether a URL is valid and safe by verifying that it has an allowed host
    and contains no harmful characters.

    :param url: The URL to validate.
    :param allowed_hosts: A set of allowed hostnames.
    :return: True if the URL is valid and safe; False otherwise.
    """

    if url and url_has_allowed_host_and_scheme(url, allowed_hosts):
        url = urlparse(url)

        harmful = ['<', '>', '"', '{', '}', '|', '\\', '^', '`', '[', ']', ';']

        if any(character in unquote(url.path) for character in harmful):
            return False

        return not any(
            character in unquote(url.query)
            for character in harmful
        )

    return False


def safe_redirect_url(request: WSGIRequest, fallback: str = '/') -> str:
    """
    Generates a safe redirect URL based on the request's GET parameters and
    HTTP_REFERER, ensuring that the URL is valid and safe. If neither the
    return URL nor the referer is valid, a fallback URL is returned.

    :param request: The WSGIRequest object containing GET and META data.
    :param fallback: The fallback URL to use if no valid redirect URL is found; defaults to '/'.
    :return: A safe redirect URL.
    """

    allowed_hosts = {request.get_host()}

    if hasattr(settings, 'ALLOWED_HOSTS'):
        allowed_hosts.update(settings.ALLOWED_HOSTS)

    return_url = request.GET.get('return_url')

    if is_url_valid_and_safe(url=return_url, allowed_hosts=allowed_hosts):
        return resolve_url(return_url)

    referer = request.META.get('HTTP_REFERER')

    if is_url_valid_and_safe(url=referer, allowed_hosts=allowed_hosts):
        url = urlparse(referer)
        query_string = urlencode(parse_qs(url.query), doseq=True)
        path = resolve_url(url.path)

        full = (
            url.scheme,
            url.netloc,
            path,
            '',
            query_string,
            url.fragment
        )

        return urlunparse(full)

    if not is_url_valid_and_safe(url=fallback, allowed_hosts=allowed_hosts):
        fallback = '/'

    return fallback
