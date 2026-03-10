from __future__ import annotations
from django_spire.api.choices import ApiPermissionChoices

import importlib

from django.apps import apps
from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.tests.api_v1 import router as test_router

api_v1 = NinjaAPI(
    title='API',
    version='1.0',
    urls_namespace='django_spire:api_v1',
    auth=[
        ApiKeySecurity(permission_required=ApiPermissionChoices.DELETE)
    ],
    throttle=[
        AnonRateThrottle('1/s'),
        AuthRateThrottle('150/s'),
    ],
)

for app_config in apps.get_app_configs():
    if hasattr(app_config, 'API_V1_ROUTER') and hasattr(app_config, 'API_V1_ROUTER_PREFIX'):
        import_parts = app_config.API_V1_ROUTER.split('.')

        if import_parts[-1] != 'router':
            message = f'{app_config.label} API_V1_ROUTER must be a router instance called `router`.'
            raise ValueError(message)

        api_v1.add_router(
            prefix=app_config.API_V1_ROUTER_PREFIX,
            router=importlib.import_module('.'.join(import_parts[:-1])).router,
            tags=[app_config.API_V1_ROUTER_PREFIX],
        )

api_v1.add_router('/test', router=test_router, tags=['test'])

