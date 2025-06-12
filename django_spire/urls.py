from typing import Sequence

from django.apps import apps
from django.urls import path, include

from django_spire.core.injection.url_injector import UrlConfInjector

app_name = 'django_spire'

def build_spire_urlpatterns(
    injectors: Sequence[UrlConfInjector] | UrlConfInjector = None,
):

    _urlpatterns = []

    for app_config in apps.get_app_configs():
        if hasattr(app_config, 'URLPATTERNS_INCLUDE') and hasattr(app_config, 'URLPATTERNS_NAMESPACE'):
            _urlpatterns.append(
                path(
                    f'{app_config.URLPATTERNS_NAMESPACE}/',
                    include(
                        app_config.URLPATTERNS_INCLUDE,
                        namespace=app_config.URLPATTERNS_NAMESPACE,
                    )
                ),
            )

    if len(_urlpatterns) == 0:
        raise Exception('You need to have at least one app installed to use Django Spire.')

    if isinstance(injectors, UrlConfInjector):
        injectors = (injectors,)

    if injectors is not None and len(injectors) > 0:
        combined_injector = UrlConfInjector()
        for injector in injectors:
            if not isinstance(injector, UrlConfInjector):
                raise TypeError(
                    f'Invalid injector passed to build_spire_urlpatterns: {injector}. '
                    f'Injectors passed to build_spire_urlpatterns must be {UrlConfInjector}'
                )

            combined_injector += injector

        _urlpatterns = combined_injector(_urlpatterns)

    return _urlpatterns

urlpatterns = build_spire_urlpatterns()

