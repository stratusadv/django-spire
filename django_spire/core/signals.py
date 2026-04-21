from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_migrate
from django.dispatch import receiver

if TYPE_CHECKING:
    from typing import Any

    from django.apps import AppConfig


@receiver(post_migrate)
def sync_site_from_settings(sender: type[AppConfig], **kwargs: Any) -> None:
    if not hasattr(settings, 'DJANGO_SITE_DOMAIN'):
        return

    site_id = getattr(settings, 'SITE_ID', 1)

    Site.objects.update_or_create(
        id=site_id,
        defaults={
            'domain': settings.DJANGO_SITE_DOMAIN,
            'name': getattr(settings, 'DJANGO_SITE_NAME', settings.DJANGO_SITE_DOMAIN),
        }
    )
