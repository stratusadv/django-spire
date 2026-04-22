from __future__ import annotations

from ninja import Router

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices
from test_project.apps.queryset_filtering.models import Task

router = Router()


@router.get("/list", auth=ApiKeySecurity(permission_required=ApiPermissionChoices.VIEW))
def add(request, status: str):
    tasks = Task.objects.filter(status=status)
    return {'tasks': [task.name for task in tasks]}
