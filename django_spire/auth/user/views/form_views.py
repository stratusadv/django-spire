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
from django_spire.auth.user.tools import add_user_to_all_user_group

from django_spire.contrib.form.tools import show_form_errors
from django_spire.history.activity.utils import add_form_activity
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_user.add_authuser')
def register_form_view(request: WSGIRequest) -> TemplateResponse:
    portal_user = AuthUser()
    Glue.model(
        request=request, unique_name='portal_user', target=portal_user, access=Glue.Access.VIEW
    )

    if request.method == 'POST':
        user_form = forms.RegisterUserForm(request.POST, instance=portal_user)

        if user_form.is_valid():
            user = user_form.save()
            add_user_to_all_user_group(user)

            add_form_activity(user, 0, request.user)

            return HttpResponseRedirect(reverse('django_spire:auth:user:page:list'))

        show_form_errors(request, user_form)
    else:
        user_form = forms.RegisterUserForm(instance=portal_user)

    context = {'request': request, 'user_form_data': json.dumps(user_form.data, cls=DjangoJSONEncoder)}
    context['page_title'] = 'Register'
    context['page_description'] = 'New User'
    context['breadcrumbs'] = [
        {'name': 'Users', 'href': reverse('django_spire:auth:user:page:list')},
        {'name': 'Register New User', 'href': None},
    ]
    return TemplateResponse(
        request, 'django_spire/auth/user/page/register_form_page.html', context=context
    )


@permission_required('django_spire_auth_user.change_authuser')
def form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    portal_user = get_object_or_404(AuthUser, pk=pk)
    Glue.model(
        request=request, unique_name='portal_user', target=portal_user, access=Glue.Access.VIEW
    )

    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=portal_user)

        if form.is_valid():
            portal_user = form.save()
            add_form_activity(portal_user, pk, request.user)

            return HttpResponseRedirect(
                reverse('django_spire:auth:user:page:detail', kwargs={'pk': pk})
            )
    else:
        form = forms.UserForm(instance=portal_user)

    context = {
        'request': request,
        'portal_user': portal_user,
        'form': form,
        'initial_data': json.dumps(form.data, cls=DjangoJSONEncoder),
        'page_title': portal_user._meta.verbose_name.title(),
        'page_description': 'Edit',
        'breadcrumbs': [
            {'name': 'Users', 'href': reverse('django_spire:auth:user:page:list')},
            {
                'name': str(portal_user),
                'href': reverse(
                    'django_spire:auth:user:page:detail', kwargs={'pk': portal_user.pk}
                ),
            },
            {'name': 'Edit', 'href': None},
        ],
    }
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

    context = {
        'request': request,
        'user': user,
        'form': forms.UserGroupForm(),
        'page_title': 'User',
        'page_description': 'Edit Groups',
        'breadcrumbs': [
            {'name': 'Users', 'href': reverse('django_spire:auth:user:page:list')},
            {
                'name': str(user),
                'href': reverse('django_spire:auth:user:page:detail', kwargs={'pk': user.pk}),
            },
            {'name': 'Edit Groups', 'href': None},
        ],
    }
    return TemplateResponse(request, 'django_spire/auth/user/page/group_form_page.html', context)
