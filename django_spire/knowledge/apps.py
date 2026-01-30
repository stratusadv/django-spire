from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.apps import AppConfig
from django.db.backends.signals import connection_created

from django_spire.utils import check_required_apps

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper


log = logging.getLogger(__name__)


def ensure_pg_trgm(sender: Any, connection: BaseDatabaseWrapper, **_kwargs: dict[str, Any]) -> None:
    if getattr(ensure_pg_trgm, '_checked', False):
        return

    if connection.vendor != 'postgresql':
        ensure_pg_trgm._checked = True
        return

    try:
        with connection.cursor() as cursor:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

        ensure_pg_trgm._checked = True
    except Exception:
        log.exception('Failed to install pg_trgm extension')


class KnowledgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_knowledge'
    name = 'django_spire.knowledge'
    MODEL_PERMISSIONS = (
        {
            'name': 'knowledge',
            'verbose_name': 'Knowledge',
            'model_class_path': 'django_spire.knowledge.collection.models.Collection',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.knowledge.urls'
    URLPATTERNS_NAMESPACE = 'knowledge'

    def ready(self) -> None:
        check_required_apps(self.label)
        connection_created.connect(ensure_pg_trgm)
