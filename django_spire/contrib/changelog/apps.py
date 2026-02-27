from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class ChangeLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_contrib_changelog'
    name = 'django_spire.contrib.changelog'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.contrib.changelog.urls'
    URLPATTERNS_NAMESPACE = 'changelog'

    def ready(self) -> None:
        check_required_apps(self.label)
