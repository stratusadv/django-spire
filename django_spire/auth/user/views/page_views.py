from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

import django_glue as dg
from django_glue.utils import serialize_to_json

from django_spire.core.redirect import safe_redirect_url
from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.contrib.form.confirmation_forms import (
    DeleteConfirmationForm,
    ConfirmationForm
)
from django_spire.contrib.form.utils import show_form_errors
from django_spire.history.activity.utils import add_form_activity
from django_spire.contrib.pagination.pagination import paginate_list
from django_spire.auth.group.decorators import permission_required
from django_spire.auth.user.models import AuthUser
from django_spire.auth.group.permissions import (
    generate_group_perm_data,
    generate_user_perm_data
)
from django_spire.auth.user import forms
from django_spire.contrib.generic_views import portal_views


def register_user_form_view(request):
    # Is this the best way to initialize a null object in glue?
    dg.glue_model_object(request, 'portal_user', AuthUser(), 'view')

    if request.method == 'POST':
        user_form = forms.RegisterUserForm(request.POST)

        # Checks to see if all forms are valid.
        if user_form.is_valid():
            user = user_form.save()

            # Add form activity. This needs to be improved.
            add_form_activity(user, 0, request.user)

            return HttpResponseRedirect(reverse('user_account:list'))

        show_form_errors(request, user_form)
    else:
        # If the form has an initial it will override the defaults.
        user_form = forms.RegisterUserForm()

    context_data = {
        # Todo: Function that takes in all of the forms and dumps the data here?
        'user_form_data': json.dumps(user_form.data, cls=DjangoJSONEncoder),
    }

    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb(name='Users', href=reverse('user_account:list'))
    crumbs.add_breadcrumb(name='Register New User')

    return portal_views.template_view(
        request,
        context_data=context_data,
        page_title='Register',
        page_description='New User',
        breadcrumbs=crumbs,
        template='django_spire/user_account/page/register_user_form_page.html'
    )


@permission_required('permission.view_portaluser')
def user_detail_page_view(request, pk):
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
        template='django_spire/user_account/page/user_detail_page.html'
    )


@permission_required('permission.view_portaluser')
def user_list_page_view(request):
    user_list = AuthUser.objects.all()

    context_data = {
        'user_list': paginate_list(user_list, page_number=request.GET.get('page', 1))
    }

    return portal_views.list_view(
        request,
        context_data=context_data,
        model=AuthUser,
        template='django_spire/user_account/page/user_list_page.html'
    )


@permission_required('permission.change_portaluser')
def user_form_page_view(request, pk):
    portal_user = get_object_or_404(AuthUser, pk=pk)
    dg.glue_model_object(request, 'portal_user', portal_user, 'view')

    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=portal_user)

        if form.is_valid():
            portal_user = form.save()
            add_form_activity(portal_user, pk, request.user)

            return HttpResponseRedirect(reverse('user_account:list'))
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
        template='django_spire/user_account/page/user_form_page.html'
    )


@permission_required('permission.delete_portaluser')
def user_status_form_page_view(request, pk):
    user = get_object_or_404(AuthUser, pk=pk)

    form_class = DeleteConfirmationForm if user.is_active else ConfirmationForm

    if request.method == 'POST':
        form = form_class(request.POST)

        if form.is_valid():
            user.is_active = not user.is_active
            user.save()

            toggle_verb = 'activated' if user.is_active else 'deactivated'

            user.add_activity(
                user=request.user,
                verb=toggle_verb,
                information=f'{request.user.get_full_name()} {toggle_verb} user "{user.get_full_name()}".'
            )

            return_url = safe_redirect_url(request)
            return HttpResponseRedirect(return_url)

    form = form_class()
    toggle_verb = 'Activate' if user.is_active else 'Deactivate'

    def update_breadcrumbs(breadcrumbs: Breadcrumbs):
        breadcrumbs.add_breadcrumb(name=toggle_verb)

    return portal_views.form_view(
        request,
        form=form,
        verb=toggle_verb,
        obj=user,
        breadcrumbs_func=update_breadcrumbs
    )


