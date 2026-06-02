from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data, generate_user_perm_data
from django_spire.auth.user.models import AuthUser
from django_spire.contrib import generic_views

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('django_spire_auth_user.view_authuser')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user = get_object_or_404(AuthUser, pk=pk)
    group_list = user.groups.all()

    context_data = {
        'user': user,
        'group_list': group_list,
        'group_list_permission_data': [generate_group_perm_data(group) for group in group_list],
        'user_perm_data': generate_user_perm_data(user),
    }

    return generic_views.detail_view(
        request,
        context_data=context_data,
        obj=user,
        template='django_spire/auth/user/page/detail_page.html',
    )


@permission_required('django_spire_auth_user.view_authuser')
def list_view(request: WSGIRequest) -> TemplateResponse:
    active_user_list = (
        AuthUser.objects.filter(is_active=True)
        .prefetch_related('groups')
        .order_by('first_name', 'last_name')
    )
    inactive_user_list = (
        AuthUser.objects.filter(is_active=False)
        .prefetch_related('groups')
        .order_by('first_name', 'last_name')
    )

    paginated_active_user_list = Paginator(active_user_list, 10).get_page(
        request.GET.get('page', 1)
    )
    paginated_inactive_user_list = Paginator(inactive_user_list, 10).get_page(
        request.GET.get('page', 1)
    )

    context_data = {
        'active_user_list': paginated_active_user_list,
        'inactive_user_list': paginated_inactive_user_list,
    }

    return generic_views.list_view(
        request,
        context_data=context_data,
        model=AuthUser,
        template='django_spire/auth/user/page/list_page.html',
    )
