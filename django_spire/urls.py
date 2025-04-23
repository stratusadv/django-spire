from django.apps import apps
from django.urls import path, include

app_name = 'django_spire'

urlpatterns = []

for app_config in apps.get_app_configs():
    if hasattr(app_config, 'URLPATTERNS_INCLUDE') and hasattr(app_config, 'URLPATTERNS_NAMESPACE'):
        urlpatterns.append(
            path(
                f'django_spire/{app_config.URLPATTERNS_NAMESPACE}/',
                include(
                    app_config.URLPATTERNS_INCLUDE,
                    namespace=app_config.URLPATTERNS_NAMESPACE,
                )
            ),
        )

if len(urlpatterns) == 0:
    raise Exception('You need to have at least one app installed to use Django Spire.')
