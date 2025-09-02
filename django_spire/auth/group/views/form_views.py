from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

import django_glue as dg
from django_spire.auth.group import models, forms
from django_spire.auth.group.decorators import permission_required
from django_spire.auth.group.utils import add_users_to_group
from django_spire.auth.user.models import AuthUser
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.generic_views import portal_views
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity


@permission_required(' permission.change_portalgroup')
def group_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    group = get_object_or_null_obj(models.AuthGroup, pk=pk)

    dg.glue_model_object(request, 'group', group)

    if request.method == 'POST':
        form = forms.GroupForm(request.POST, instance=group)

        if form.is_valid():
            group = form.save()
            add_form_activity(group, pk, request.user)

            return_url = reverse('django_spire:auth:group:page:list')
            return HttpResponseRedirect(return_url)

    form = forms.GroupForm(instance=group)

    context_data = {'group': group}

    return portal_views.model_form_view(
        request,
        form=form,
        context_data=context_data,
        template='django_spire/auth/group/page/form_page.html',
        obj=group,
    )


@permission_required('permission.add_portalgroup')
def group_user_form_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    group = get_object_or_404(models.AuthGroup, pk=pk)
    user_choices = AuthUser.services.get_user_choices()

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

            return_url = reverse('permission:detail', kwargs={'pk': pk})
            return HttpResponseRedirect(return_url)

    form = forms.GroupUserForm(group=group)

    def crumbs(breadcrumbs) -> None:
        breadcrumbs.add_breadcrumb(name='Add Users')

    context_data = {
        'group': group,
        'user_choices': user_choices
    }

    return portal_views.form_view(
        request,
        form=form,
        obj=group,
        template='django_spire/auth/group/page/group_user_form_page.html',
        context_data=context_data,
        breadcrumbs_func=crumbs,
    )


@permission_required('permission.delete_portalgroup')
def group_delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.AuthGroup, pk=pk)
    return_url = reverse('permission:list')

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
    group = get_object_or_404(models.AuthGroup, pk=group_pk)
    user = get_object_or_404(AuthUser, pk=pk)

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST, obj=user)

        if form.is_valid():
            user.groups.remove(group)

            group.add_activity(
                user=request.user,
                verb='removed',
                information=f'{request.user.get_full_name()} removed {user.get_full_name()} from the group "{group.name}".'
            )

            return_url = reverse('permission:detail', kwargs={'pk': group_pk})
            return HttpResponseRedirect(return_url)

    form = DeleteConfirmationForm(request.GET, obj=user)

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
