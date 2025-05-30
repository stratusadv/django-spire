from django.apps import AppConfig


class DjangoSpireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_core'
    name = 'django_spire.core'

    URLPATTERNS_INCLUDE = 'django_spire.core.urls'
    URLPATTERNS_NAMESPACE = 'core'
