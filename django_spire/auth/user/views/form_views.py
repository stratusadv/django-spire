from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.user import forms
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.navigation import AuthUserNavigation
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_user.change_authuser')
def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    portal_user = get_object_or_null_obj(AuthUser, pk=pk)

    form = forms.UserForm(request.POST or None, instance=portal_user)

    Glue.form(request, unique_name='user_form', target=form, access=Glue.Access.CHANGE)

    nav = AuthUserNavigation()
    nav.set_page_title_from_model_name(portal_user)

    if portal_user.pk:
        nav.breadcrumbs.add_model_instance_string(
            portal_user,
            view_name='django_spire:auth:user:page:detail',
            view_kwargs={'pk': portal_user.pk},
        )

    nav.breadcrumbs.add(f'Edit' if portal_user.pk else 'New User (With Glue)')

    context = nav.as_context()

    return TemplateResponse(request, 'django_spire/auth/user/page/form_page.html', context)


@permission_required('django_spire_auth_group.change_authgroup')
def group_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user = get_object_or_404(AuthUser, pk=pk)
    Glue.queryset(
        request=request,
        unique_name='group_choices',
        target=AuthGroup.objects.all(),
        fields='__all__',
    )

    if request.method == 'POST':
        form = forms.UserGroupForm(request.POST)

        if form.is_valid():
            user.groups.set(form.cleaned_data['group_list'])
            return HttpResponseRedirect(
                reverse('django_spire:auth:user:page:detail', kwargs={'pk': pk})
            )

        show_form_errors(request, form)

    form = forms.UserGroupForm()

    nav = AuthUserNavigation()
    nav.page_title = 'User'
    nav.breadcrumbs.add_model_instance_string(
        user, view_name='django_spire:auth:user:page:detail', view_kwargs={'pk': user.pk}
    )
    nav.breadcrumbs.add('Edit Groups')

    context = nav.as_context()
    context['user'] = user
    context['form'] = form
    return TemplateResponse(request, 'django_spire/auth/user/page/group_form_page.html', context)


@permission_required('django_spire_auth_user.change_authuser')
def reset_password_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user = get_object_or_404(AuthUser, pk=pk)

    nav = AuthUserNavigation()
    nav.page_title = 'Reset Password'
    nav.breadcrumbs.add('Users', 'django_spire:auth:user:page:list')
    nav.breadcrumbs.add_model_instance_string(
        user, view_name='django_spire:auth:user:page:detail', view_kwargs={'pk': user.pk}
    )
    nav.breadcrumbs.add('Reset Password')

    context = nav.as_context()
    context['user'] = user

    if request.method == 'POST':
        new_password = user.services.random_reset_password()
        context['password_reset_complete'] = True
        context['new_password'] = new_password
    else:
        context['password_reset_complete'] = False

    return TemplateResponse(
        request,
        'django_spire/auth/user/page/reset_password_page.html',
        context,
    )
