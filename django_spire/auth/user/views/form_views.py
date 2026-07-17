from __future__ import annotations

import json

from django_glue import Glue

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.user import forms
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.navigation import AuthUserNavigation
from django_spire.auth.user.tools import add_user_to_all_user_group

from django_spire.contrib.form.tools import show_form_errors
from django_spire.history.activity.utils import add_form_activity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_user.add_authuser')
def register_form_view(request: WSGIRequest) -> TemplateResponse:
    portal_user = AuthUser()

    form = forms.UserForm(instance=portal_user)

    Glue.form(request, unique_name='user_form', target=form, access=Glue.Access.CHANGE)

    nav = AuthUserNavigation()
    nav.page_title = 'Register'
    nav.page_description = 'New User'
    nav.breadcrumbs.add('Users', 'django_spire:auth:user:page:list')
    nav.breadcrumbs.add('Register New User')

    context = nav.as_context()

    return TemplateResponse(
        request, 'django_spire/auth/user/page/register_form_page.html', context=context
    )


@permission_required('django_spire_auth_user.change_authuser')
def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    portal_user = get_object_or_404(AuthUser, pk=pk)

    form = forms.UserForm(instance=portal_user)

    Glue.form(request, unique_name='user_form', target=form, access=Glue.Access.CHANGE)

    # Glue.model(
    #     request=request, unique_name='portal_user', target=portal_user, access=Glue.Access.VIEW
    # )
    #
    # if request.method == 'POST':
    #     form = forms.UserForm(request.POST, instance=portal_user)
    #
    #     if form.is_valid():
    #         portal_user = form.save()
    #         add_form_activity(portal_user, pk, request.user)
    #
    #         return HttpResponseRedirect(
    #             reverse('django_spire:auth:user:page:detail', kwargs={'pk': pk})
    #         )
    # else:
    #     form = forms.UserForm(instance=portal_user)

    nav = AuthUserNavigation()
    nav.page_description = 'Edit'
    nav.set_page_title_from_model_name(portal_user)
    nav.breadcrumbs.add('Users', 'django_spire:auth:user:page:list')
    nav.breadcrumbs.add_model_instance_string(
        portal_user,
        view_name='django_spire:auth:user:page:detail',
        view_kwargs={'pk': portal_user.pk},
    )
    nav.breadcrumbs.add('Edit')

    context = nav.as_context()
    # context['portal_user'] = portal_user
    # context['form'] = form
    # context['initial_data'] = json.dumps(form.data, cls=DjangoJSONEncoder)
    # context['form_title'] = f'Edit {portal_user}'
    # context['form_description'] = 'Update user information.'
    return TemplateResponse(request, 'django_spire/auth/user/page/form_page.html', context)


@permission_required('django_spire_auth_group.change_authgroup')
def group_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    user = get_object_or_404(AuthUser, pk=pk)
    Glue.queryset(request=request, unique_name='group_choices', target=AuthGroup.objects.all())

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
    nav.page_description = 'Edit Groups'
    nav.breadcrumbs.add('Users', 'django_spire:auth:user:page:list')
    nav.breadcrumbs.add_model_instance_string(
        user, view_name='django_spire:auth:user:page:detail', view_kwargs={'pk': user.pk}
    )
    nav.breadcrumbs.add('Edit Groups')

    context = nav.as_context()
    context['user'] = user
    context['form'] = form
    context['form_title'] = f'Edit Groups for {user}'
    context['form_description'] = 'Manage group membership for this user.'
    return TemplateResponse(request, 'django_spire/auth/user/page/group_form_page.html', context)
