from __future__ import annotations

import hashlib

from django_spire.conf import settings


def get_theme_cookie_name() -> str:
    if not hasattr(settings, 'BASE_DIR'):
        return 'django-spire-theme'

    encoded = str(settings.BASE_DIR).encode()
    identifier = hashlib.md5(encoded, usedforsecurity=False).hexdigest()[:8]
    return f'django-spire-theme-{identifier}'
