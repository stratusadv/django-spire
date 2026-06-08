from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data, generate_user_perm_data
from django_spire.auth.user.models import AuthUser


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


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

    context_data['page_title'] = str(user)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Users', 'href': reverse('django_spire:auth:user:page:list')},
        {'name': str(user), 'href': None},
    ]
    return TemplateResponse(
        request, context=context_data, template='django_spire/auth/user/page/detail_page.html'
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

    context_data['page_title'] = 'User'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'Users', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='django_spire/auth/user/page/list_page.html'
    )
