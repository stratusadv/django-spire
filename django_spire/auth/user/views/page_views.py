from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data, generate_user_perm_data
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.navigation import AuthUserNavigation


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_user.view_authuser')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user = get_object_or_404(AuthUser, pk=pk)
    group_list = user.groups.all()

    nav = AuthUserNavigation()
    nav.page_title = str(user)
    nav.breadcrumbs.add_model_instance_string(
        user, view_name='django_spire:auth:user:page:detail', view_kwargs={'pk': user.pk}
    )

    context = nav.as_context()
    context['user'] = user
    context['group_list'] = group_list
    context['group_list_permission_data'] = [
        generate_group_perm_data(group) for group in group_list
    ]
    context['user_perm_data'] = generate_user_perm_data(user)
    return TemplateResponse(
        request, context=context, template='django_spire/auth/user/page/detail_page.html'
    )


@permission_required('django_spire_auth_user.view_authuser')
def list_view(request: WSGIRequest) -> TemplateResponse:
    active_users = (
        AuthUser.objects.filter(is_active=True)
        .prefetch_related('groups')
        .order_by('first_name', 'last_name')
    )
    inactive_users = (
        AuthUser.objects.filter(is_active=False)
        .prefetch_related('groups')
        .order_by('first_name', 'last_name')
    )

    Glue.queryset(request, 'active_users', active_users, Glue.Access.VIEW, fields='__all__')
    Glue.queryset(request, 'inactive_users', inactive_users, Glue.Access.VIEW, fields='__all__')

    nav = AuthUserNavigation()
    nav.page_title = 'Users'

    context = nav.as_context()
    context['active_users'] = active_users
    context['active_user_count'] = active_users.count()
    context['inactive_users'] = inactive_users
    context['inactive_user_count'] = inactive_users.count()
    return TemplateResponse(
        request, context=context, template='django_spire/auth/user/page/list_page.html'
    )
