from __future__ import annotations

import base64

import requests

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile


class HtmlRendererClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url or settings.HTML_RENDERER_URL
        self.api_key = api_key or settings.HTML_RENDERER_ACCESS_KEY

    def _request(self, endpoint: str, media_url: str, **kwargs) -> bytes:
        session = requests.Session()

        response = session.request(
            method='POST',
            url=f'{self.base_url}/{endpoint}/',
            headers={
                'x-api-key': self.api_key,
            },
            json={'media_url': media_url, **kwargs},
        )

        response.raise_for_status()

        return base64.b64decode(response.json())

    @staticmethod
    def get_site_url() -> str:
        if settings.DEBUG:
            return f'http://host.docker.internal:{settings.HTML_RENDERER_PORT}'

        return f'https://{Site.objects.get_current()}'

    def html_to_pdf(self, media_url: str, file_name: str) -> InMemoryUploadedFile:
        file = self._request('html_to_pdf', media_url)

        return InMemoryUploadedFile(
            file=ContentFile(file),
            field_name='html_renderer',
            name=file_name,
            content_type='application/pdf',
            size=len(file),
            charset=None,
        )

    def html_to_png(
        self,
        media_url: str,
        file_name: str,
        screen_width: int = -1,
        screen_height: int = -1,
    ) -> InMemoryUploadedFile:
        file = self._request(
            'html_to_png',
            media_url,
            screen_width=screen_width,
            screen_height=screen_height,
        )

        return InMemoryUploadedFile(
            file=ContentFile(file),
            field_name='html_renderer',
            name=file_name,
            content_type='image/png',
            size=len(file),
            charset=None,
        )
