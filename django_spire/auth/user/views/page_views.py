from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

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
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add('Users', reverse('django_spire:auth:user:page:list'))
    nav.breadcrumbs.add_model_instance_string(
        user, url='django_spire:auth:user:page:detail', url_kwargs={'pk': user.pk}
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

    nav = AuthUserNavigation()
    nav.page_title = 'Users'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Users')

    context = nav.as_context()
    context['active_user_list'] = paginated_active_user_list
    context['inactive_user_list'] = paginated_inactive_user_list
    return TemplateResponse(
        request, context=context, template='django_spire/auth/user/page/list_page.html'
    )


@permission_required('django_spire_auth_user.view_authuser')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    user_list = AuthUser.objects.filter(is_active=True).order_by('username')

    paginated_user_list = Paginator(user_list, 25).get_page(request.GET.get('page', 1))

    nav = AuthUserNavigation()
    nav.page_title = 'API Access'
    nav.page_description = 'Manage API access for users'
    nav.breadcrumbs.add('Users', reverse('django_spire:auth:user:page:list'))
    nav.breadcrumbs.add('API Access')

    context = nav.as_context()
    context['user_list'] = paginated_user_list
    return TemplateResponse(
        request, context=context, template='django_spire/auth/user/page/access_list_page.html'
    )
