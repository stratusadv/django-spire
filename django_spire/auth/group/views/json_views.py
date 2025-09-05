from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from django_spire.auth.group import models
from django_spire.auth.group.utils import perm_level_to_int, perm_level_to_django_permission
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.permissions import GroupPermissions
from django_spire.auth.permissions.tools import generate_model_permissions, generate_model_key_permission_map
from django_spire.core.shortcuts import process_request_body


@require_POST
@permission_required('django_spire_auth_group.change_authgroup')
def permission_form_ajax(
    request: WSGIRequest,
    pk: int,
    app_name: str
) -> JsonResponse:
    if request.method == 'POST':
        error_message = 'App Does Not Exist.'

        permission_map = generate_model_key_permission_map()

        if app_name.lower() in permission_map:
            model_permission = permission_map[app_name.lower()]
            body = process_request_body(request, key=None)
            perm_level = perm_level_to_int(body.get('perm_level'))
            error_message = 'Please provide a valid permission level'

            if isinstance(perm_level, int) and 4 >= perm_level >= 0:
                group = get_object_or_404(models.AuthGroup, pk=pk)
                group_perm_helper = GroupPermissions(group, model_permission=model_permission)

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
@permission_required('django_spire_auth_group.change_authgroup')
def special_role_form_ajax(
    request: WSGIRequest,
    pk: int,
    app_name: str
) -> JsonResponse:
    if request.method == 'POST':
        error_message = 'App Does Not Exist.'

        permission_map = generate_model_key_permission_map()

        if app_name.lower() in permission_map:
            model_permission = permission_map[app_name.lower()]
            body = process_request_body(request, key=None)
            grant_special_role_access = body.get('grant_special_role_access')
            codename = body.get('codename')
            error_message = 'models.PortalUser does not have permission.'

            if request.user.has_perm('django_spire_auth_group.change_authgroup'):
                group = get_object_or_404(models.AuthGroup, pk=pk)
                group_perm_helper = GroupPermissions(group, model_permission=model_permission)

                if grant_special_role_access:
                    group_perm_helper.add_special_role(codename)
                else:
                    group_perm_helper.remove_special_role(codename)

                return JsonResponse({'message': 'Updated Successfully!', 'status': 200})

    return JsonResponse({'message': error_message, 'status': 400})
