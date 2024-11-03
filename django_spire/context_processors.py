from __future__ import annotations

from django_spire import __version__


def spire(request) -> dict[str, str]:
    return {'DJANGO_SPIRE_VERSION': __version__}
