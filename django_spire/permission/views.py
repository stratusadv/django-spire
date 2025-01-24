from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from django_spire.permission.models import PortalUser
from django_spire.views import portal_views
from django_spire.forms import DeleteConfirmationForm
from django_spire.core.shortcuts import (
    get_object_or_null_obj,
    process_request_body
)
from django_spire.redirect import safe_redirect_url
from django_spire.history.utils import add_form_activity
from django_spire.permission.constants import PERMISSION_MODELS_DICT
from django_spire.permission.decorators import permission_required
from django_spire.permission import forms, models
from django_spire.permission.permissions import (
    generate_group_perm_data,
    GroupPermissions
)
from django_spire.permission.utils import (
    add_users_to_group,
    perm_level_to_int,
    perm_level_to_django_permission
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@permission_required('permission.view_portalgroup')
def group_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.PortalGroup, pk=pk)

    context_data = {
        'group': group,
        'permission_data': generate_group_perm_data(group, with_special_role=True),
        'user_list': group.user_set.all()
    }

    return portal_views.detail_view(
        request,
        context_data=context_data,
        obj=group,
        template='spire/permission/page/group_detail_page.html'
    )


@permission_required('permission.view_portalgroup')
def group_list_view(request: WSGIRequest) -> TemplateResponse:
    group_list = models.PortalGroup.objects.all().prefetch_related('permissions')

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
        model=models.PortalGroup,
        template='spire/permission/page/group_list_page.html'
    )


@permission_required('permission.change_portalgroup')
def group_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_null_obj(models.PortalGroup, pk=pk)

    if request.method == 'POST':
        form = forms.GroupForm(request.POST, instance=group)

        if form.is_valid():
            group = form.save()
            add_form_activity(group, pk, request.user)
            return_url = safe_redirect_url(request)
            return HttpResponseRedirect(return_url)

    form = forms.GroupForm(instance=group)

    context_data = {'group': group}

    return portal_views.model_form_view(
        request,
        form=form,
        context_data=context_data,
        obj=group,
    )


@permission_required('permission.add_portalgroup')
def group_user_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.PortalGroup, pk=pk)

    if request.method == 'POST':
        form = forms.GroupUserForm(request.POST, group=group)

        if form.is_valid():
            user_list = form.cleaned_data.get('available_users')
            add_users_to_group(group, user_list)
            group.add_activity(
                user=request.user,
                verb='added',
                information=f'{request.user.get_full_name()} added {len(user_list)} users to the group "{group.name}".'
            )
            return_url = safe_redirect_url(request)
            return HttpResponseRedirect(return_url)

    form = forms.GroupUserForm(group=group)

    def crumbs(breadcrumbs) -> None:
        breadcrumbs.add_breadcrumb(name='Add Users')

    context_data = {'form_description': ''}

    return portal_views.form_view(
        request,
        form=form,
        obj=group,
        context_data=context_data,
        breadcrumbs_func=crumbs,
    )


@permission_required('permission.delete_portalgroup')
def group_delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.PortalGroup, pk=pk)
    return_url = safe_redirect_url(request)

    return portal_views.delete_form_view(
        request,
        obj=group,
        delete_func=group.delete,
        return_url=return_url
    )


@permission_required('permission.delete_portaluser')
def group_remove_user_form_view(
    request: WSGIRequest,
    group_pk: int,
    pk: int
) -> HttpResponseRedirect | TemplateResponse:
    group = get_object_or_404(models.PortalGroup, pk=group_pk)
    user = get_object_or_404(PortalUser, pk=pk)

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST)
        if form.is_valid():
            user.groups.remove(group)
            group.add_activity(
                user=request.user,
                verb='removed',
                information=f'{request.user.get_full_name()} removed {user.get_full_name()} from the group "{group.name}".'
            )
            return_url = safe_redirect_url(request)
            return HttpResponseRedirect(return_url)

    form = DeleteConfirmationForm()

    def get_breadcrumbs(breadcrumbs) -> None:
        breadcrumbs = group.breadcrumbs()
        breadcrumbs.add_breadcrumb(name=user.get_full_name())
        breadcrumbs.add_breadcrumb(name='Remove')

    return portal_views.form_view(
        request,
        form=form,
        verb=f'remove {user.get_full_name()} from',
        obj=group,
        breadcrumbs_func=get_breadcrumbs
    )


@require_POST
@permission_required('permission.change_portalgroup')
def group_permission_form_ajax(
    request: WSGIRequest,
    pk: int,
    app_name: str
) -> JsonResponse:
    if request.method == 'POST':
        error_message = 'App Does Not Exist.'

        if app_name.lower() in PERMISSION_MODELS_DICT:
            body = process_request_body(request)
            perm_level = perm_level_to_int(body.get('perm_level'))
            error_message = 'Please provide a valid permission level'

            if isinstance(perm_level, int) and 4 >= perm_level >= 0:
                group = get_object_or_404(models.PortalGroup, pk=pk)
                group_perm_helper = GroupPermissions(group, model_key=app_name)

                django_permission_verbose = perm_level_to_django_permission(
                    perm_level=perm_level,
                    app_label=group_perm_helper.model_permissions.app_label,
                    model_name=group_perm_helper.model_permissions.model_name
                )

                error_message = 'You do not have permission to change this app.'

                if request.user.has_perm(django_permission_verbose) or perm_level == 0:
                    group_perm_helper.update_perms(perm_level)
                    return JsonResponse({'message': 'Updated Successfully!', 'status': 200})

        return JsonResponse({'message': error_message, 'status': 400})


@require_POST
@permission_required('permission.change_portalgroup')
def group_special_role_form_ajax(
    request: WSGIRequest,
    pk: int,
    app_name: str
) -> JsonResponse:
    if request.method == 'POST':
        error_message = 'App Does Not Exist.'

        if app_name.lower() in PERMISSION_MODELS_DICT:
            body = process_request_body(request)
            grant_special_role_access = body.get('grant_special_role_access')
            codename = body.get('codename')
            error_message = 'models.PortalUser does not have permission.'

            if request.user.has_perm('permission.change_portalgroup'):
                group = get_object_or_404(models.PortalGroup, pk=pk)
                group_perm_helper = GroupPermissions(group, model_key=app_name)

                if grant_special_role_access:
                    group_perm_helper.add_special_role(codename)
                else:
                    group_perm_helper.remove_special_role(codename)

                return JsonResponse({'message': 'Updated Successfully!', 'status': 200})

        return JsonResponse({'message': error_message, 'status': 400})
