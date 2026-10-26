from __future__ import annotations

import importlib.metadata

from django import __version__ as django_version
from django.contrib import admin

from django_spire import constants


def _package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def admin_site_title() -> str:
    parts = [f'Django {django_version}', f'Spire {constants.__VERSION__}']

    glue_version = _package_version('django-glue')

    if glue_version:
        parts.append(f'Glue {glue_version}')

    return f'{" ".join(parts)} Admin Panel'


def apply_admin_site_title() -> None:
    title = admin_site_title()
    admin.site.site_header = title
    admin.site.site_title = title
