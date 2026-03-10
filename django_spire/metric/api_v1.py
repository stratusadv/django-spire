from __future__ import annotations

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices

router = Router()


@router.get("/add", auth=ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW))
def add(request, a: int, b: int):
    return {"result": a + b}