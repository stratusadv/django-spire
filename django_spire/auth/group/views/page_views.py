from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.group import models
from django_spire.auth.group.navigation import AuthGroupNavigation
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_group.view_authgroup')
def detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.AuthGroup, pk=pk)

    active_user_list = group.user_set.filter(is_active=True).order_by('first_name', 'last_name')
    inactive_user_list = group.user_set.filter(is_active=False).order_by('first_name', 'last_name')

    paginated_active_user_list = Paginator(active_user_list, 10).get_page(
        request.GET.get('page', 1)
    )
    paginated_inactive_user_list = Paginator(inactive_user_list, 10).get_page(
        request.GET.get('page', 1)
    )

    nav = AuthGroupNavigation()
    nav.page_title = str(group)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
    nav.breadcrumbs.add_model_instance_breadcrumb(
        group, url='django_spire:auth:group:page:detail', url_kwargs={'pk': group.pk}
    )

    context = nav.as_context()
    context['group'] = group
    context['permission_data'] = generate_group_perm_data(group, with_special_role=True)
    context['active_user_list'] = paginated_active_user_list
    context['inactive_user_list'] = paginated_inactive_user_list
    return TemplateResponse(
        request, context=context, template='django_spire/auth/group/page/detail_page.html'
    )


@permission_required('django_spire_auth_group.view_authgroup')
def list_view(request: WSGIRequest) -> TemplateResponse:
    group_list = models.AuthGroup.objects.all().prefetch_related('permissions').order_by('name')

    nav = AuthGroupNavigation()
    nav.page_title = 'Groups'
    nav.page_description = 'List View'
    nav.breadcrumbs.add_breadcrumb('Groups')

    context = nav.as_context()
    context['group_list'] = group_list
    context['group_list_permission_data'] = [
        generate_group_perm_data(group) for group in group_list
    ]
    return TemplateResponse(
        request, context=context, template='django_spire/auth/group/page/list_page.html'
    )
