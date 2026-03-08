from __future__ import annotations

import importlib

from django.apps import apps
from ninja import NinjaAPI

from django_spire.api.auth.security import ApiKeyQuerySecurity, ApiKeyHeaderSecurity

api_v1 = NinjaAPI(
    title='API',
    version='1.0',
    urls_namespace='django_spire:api_v1',
    auth=[
        ApiKeyQuerySecurity(),
        ApiKeyHeaderSecurity()
    ]
)

for app_config in apps.get_app_configs():
    if hasattr(app_config, 'URLPATTERNS_API_V1') and hasattr(app_config, 'URLPATTERNS_API_V1_PREFIX'):
        api_v1.add_router(
            prefix=app_config.URLPATTERNS_API_V1_PREFIX,
            router=importlib.import_module(app_config.URLPATTERNS_API_V1).router,
            tags=[app_config.URLPATTERNS_API_V1_PREFIX]
        )
