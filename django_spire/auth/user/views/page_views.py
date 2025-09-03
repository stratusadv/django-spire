from __future__ import annotations

from django.shortcuts import get_object_or_404

from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.permissions.tools import generate_group_perm_data, generate_user_perm_data
from django_spire.contrib.pagination.pagination import paginate_list
from django_spire.auth.user.models import AuthUser
from django_spire.contrib.generic_views import portal_views


@permission_required('django_spire_auth_user.view_authuser')
def detail_view(request, pk):
    user = get_object_or_404(AuthUser, pk=pk)
    group_list = user.groups.all()

    context_data = {
        'user': user,
        'group_list': group_list,
        'group_list_permission_data': [generate_group_perm_data(group) for group in group_list],
        'user_perm_data': generate_user_perm_data(user)
    }

    return portal_views.detail_view(
        request,
        context_data=context_data,
        obj=user,
        template='django_spire/auth/user/page/detail_page.html'
    )


@permission_required('django_spire_auth_user.view_authuser')
def list_view(request):
    user_list = AuthUser.objects.all()

    context_data = {
        'user_list': paginate_list(user_list, page_number=request.GET.get('page', 1))
    }

    return portal_views.list_view(
        request,
        context_data=context_data,
        model=AuthUser,
        template='django_spire/auth/user/page/list_page.html'
    )
