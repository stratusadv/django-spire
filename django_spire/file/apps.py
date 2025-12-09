from __future__ import annotations

from django.apps import AppConfig
from django.conf import settings

from django_spire.utils import check_required_apps


class FileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_file'
    name = 'django_spire.file'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.file.urls'
    URLPATTERNS_NAMESPACE = 'file'

    def ready(self) -> None:
        if not hasattr(settings, 'BASE_FOLDER_NAME'):
            raise ValueError(
                f'"BASE_FOLDER_NAME" must be set in the django settings when '
                f'using "{self.label}".'
            )

        if not isinstance(settings.BASE_FOLDER_NAME, str):
            raise TypeError(
                f'"BASE_FOLDER_NAME" must be a string in the django settings when '
                f'using "{self.label}".'
            )

        check_required_apps(self.label)
