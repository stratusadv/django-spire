from __future__ import annotations

import json

import django_glue as dg
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_glue.utils import serialize_to_json

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.user import forms
from django_spire.auth.user.models import AuthUser
from django_spire.contrib import Breadcrumbs
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm, ConfirmationForm
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import portal_views
from django_spire.core.redirect import safe_redirect_url
from django_spire.history.activity.utils import add_form_activity


@permission_required('django_spire_auth_user.add_authuser')
def register_form_view(request):
    portal_user = AuthUser()
    dg.glue_model_object(request, 'portal_user', portal_user, 'view')

    if request.method == 'POST':
        user_form = forms.RegisterUserForm(request.POST, instance=portal_user)

        if user_form.is_valid():
            user = user_form.save()

            add_form_activity(user, 0, request.user)

            return HttpResponseRedirect(reverse('django_spire:auth:user:page:list'))

        show_form_errors(request, user_form)
    else:
        user_form = forms.RegisterUserForm(instance=portal_user)

    context_data = {
        # Todo: Function that takes in all of the forms and dumps the data here?
        'user_form_data': json.dumps(user_form.data, cls=DjangoJSONEncoder),
    }

    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb(name='Users', href=reverse('django_spire:auth:user:page:list'))
    crumbs.add_breadcrumb(name='Register New User')

    return portal_views.template_view(
        request,
        context_data=context_data,
        page_title='Register',
        page_description='New User',
        breadcrumbs=crumbs,
        template='django_spire/auth/user/page/register_form_page.html'
    )


@permission_required('django_spire_auth_user.change_authuser')
def form_view(request, pk):
    portal_user = get_object_or_404(AuthUser, pk=pk)
    dg.glue_model_object(request, 'portal_user', portal_user, 'view')

    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=portal_user)

        if form.is_valid():
            portal_user = form.save()
            add_form_activity(portal_user, pk, request.user)

            return HttpResponseRedirect(reverse('django_spire:auth:user:page:detail', kwargs={'pk': pk}))
    else:
        form = forms.UserForm(instance=portal_user)

    context_data = {
        'portal_user': portal_user,
        'initial_data': serialize_to_json(form.data)
    }

    return portal_views.model_form_view(
        request,
        form=form,
        obj=portal_user,
        context_data=context_data,
        template='django_spire/auth/user/page/form_page.html'
    )


@permission_required('django_spire_auth_group.change_authgroup')
def group_form_view(request, pk):
    user = get_object_or_404(AuthUser, pk=pk)
    dg.glue_query_set(request, 'group_choices', AuthGroup.objects.all())
    selected_group_ids = [group.pk for group in user.groups.all()]

    if request.method == 'POST':
        form = forms.UserGroupForm(request.POST)

        if form.is_valid():
            user.groups.set(form.cleaned_data['group_list'])
            return HttpResponseRedirect(reverse('django_spire:auth:user:page:detail', kwargs={'pk': pk}))
        else:
            show_form_errors(request, form)

    form = forms.UserGroupForm()

    context_data = {
        'user': user,
        'selected_group_ids': selected_group_ids
    }

    return portal_views.form_view(
        request,
        obj=user,
        context_data=context_data,
        form=forms.UserGroupForm(),
        template='django_spire/auth/user/page/group_form_page.html'
    )
