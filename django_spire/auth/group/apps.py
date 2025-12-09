from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class AuthGroupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_auth_group'
    name = 'django_spire.auth.group'

    REQUIRED_APPS = ('django_spire_core', 'django_spire_auth')

    MODEL_PERMISSIONS = (
        {
            'name': 'group',
            'model_class_path': 'django_spire.auth.group.models.AuthGroup',
            'is_proxy_model': True
        },
    )

    def ready(self) -> None:
        check_required_apps(self.label)
