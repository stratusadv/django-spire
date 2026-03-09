from __future__ import annotations

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiAccessLevelChoices
from test_project.apps.queryset_filtering.models import Task

router = Router()


@router.get("/list", auth=ApiKeySecurity(access_level_required=ApiAccessLevelChoices.VIEW))
def add(request, status: str):
    tasks = Task.objects.filter(status=status)
    return {'tasks': [task.name for task in tasks]}
