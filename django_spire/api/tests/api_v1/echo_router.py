from __future__ import annotations
from django.http import HttpRequest

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices

echo_router = Router()


@echo_router.get("", auth=ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW))
def echo(request: HttpRequest, value: str) -> str:
    return f'Echo "{value}" '

