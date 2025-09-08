from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django_spire.auth.group import models
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data
from django_spire.contrib.generic_views import portal_views

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('django_spire_auth_group.view_authgroup')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.AuthGroup, pk=pk)

    context_data = {
        'group': group,
        'permission_data': generate_group_perm_data(group, with_special_role=True),
        'user_list': group.user_set.all()
    }

    return portal_views.detail_view(
        request,
        context_data=context_data,
        obj=group,
        template='django_spire/auth/group/page/detail_page.html'
    )


@permission_required('django_spire_auth_group.view_authgroup')
def list_view(request: WSGIRequest) -> TemplateResponse:
    group_list = models.AuthGroup.objects.all().prefetch_related('permissions')

    context_data = {
        'group_list': group_list,
        'group_list_permission_data': [
            generate_group_perm_data(group)
            for group in group_list
        ]
    }

    return portal_views.list_view(
        request,
        context_data=context_data,
        model=models.AuthGroup,
        template='django_spire/auth/group/page/list_page.html'
    )
