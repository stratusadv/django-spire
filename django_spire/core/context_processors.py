from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any

from django_spire.consts import __VERSION__

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def django_spire(_: WSGIRequest) -> dict[str, Any]:
    # def installed_apps_context(request):
    #     return {'installed_apps': [app.label for app in apps.get_app_configs()]}

    return {
        'DJANGO_SPIRE_VERSION': __VERSION__,
        'app_bootstrap_icon': {
            'help_desk': 'bi bi-headset'
        },
        'INSTALLED_APPS': 'django_spire'
    }
