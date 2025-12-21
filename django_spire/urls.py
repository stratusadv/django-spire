from __future__ import annotations

from django.apps import apps
from django.urls import include, path

from django_spire.exceptions import DjangoSpireConfigurationError


app_name = 'django_spire'

urlpatterns = [
    path(
        f'{app_config.URLPATTERNS_NAMESPACE}/',
        include(
            app_config.URLPATTERNS_INCLUDE,
            namespace=app_config.URLPATTERNS_NAMESPACE,
        )
    )
    for app_config in apps.get_app_configs()
    if hasattr(app_config, 'URLPATTERNS_INCLUDE') and hasattr(app_config, 'URLPATTERNS_NAMESPACE')
]

if not urlpatterns:
    message = 'You need to have at least one app installed to use Django Spire.'
    raise DjangoSpireConfigurationError(message)
