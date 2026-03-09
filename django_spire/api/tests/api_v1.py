from __future__ import annotations

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiAccessLevelChoices

router = Router()


@router.get("", auth=ApiKeySecurity(access_level_required=ApiAccessLevelChoices.VIEW))
def test(request, value: str) -> str:
    return f'Test API successfully called with "{value}" as a value.'

