from django.apps import AppConfig

from django_spire.utils import check_required_apps


class FileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_file'
    name = 'django_spire.file'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.file.urls'
    URLPATTERNS_NAMESPACE = 'file'

    def ready(self) -> None:
        check_required_apps(self.label)
