from django.apps import AppConfig

from django_spire.utils import check_required_apps


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_auth'
    name = 'django_spire.auth'

    REQUIRED_APPS = ('django_spire_core',)
    
    URLPATTERNS_INCLUDE = 'django_spire.auth.urls'
    URLPATTERNS_NAMESPACE = 'auth'

    def ready(self) -> None:
        check_required_apps(self.label)