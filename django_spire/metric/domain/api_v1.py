from __future__ import annotations

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices
from django_spire.metric.domain.statistic.api_v1 import router as statistic_router

router = Router()

router.add_router('statistic', statistic_router)


@router.get('/subtract', auth=ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW))
def subtract(request, a: int, b: int):
    return {'result': a - b}
