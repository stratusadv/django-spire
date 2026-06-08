from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.group import models, forms
from django_spire.auth.group.navigation import AuthGroupNavigation
from django_spire.auth.group.utils import set_group_users
from django_spire.auth.permissions.decorators import permission_required
from django_spire.auth.user.models import AuthUser
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.utils import add_form_activity

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_auth_group.change_authgroup')
def form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    group = get_object_or_null_obj(models.AuthGroup, pk=pk)

    if request.method == 'POST':
        form = forms.GroupForm(request.POST, instance=group)

        if form.is_valid():
            group = form.save()
            add_form_activity(group, pk, request.user)

            return_url = reverse('django_spire:auth:group:page:list')
            return HttpResponseRedirect(return_url)

        show_form_errors(request, form)

    form = forms.GroupForm(instance=group)

    nav = AuthGroupNavigation()
    nav.set_page_title_from_model_name(group)
    nav.page_description = 'Edit' if group.pk else 'Create'
    nav.breadcrumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
    nav.breadcrumbs.add_breadcrumb('Edit' if group.pk else 'Create')

    context = nav.as_context()
    context['form'] = form
    context['group'] = group
    return TemplateResponse(
        request, context=context, template='django_spire/auth/group/page/form_page.html'
    )


@permission_required('django_spire_auth_group.add_authgroup')
def user_form_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    group = get_object_or_404(models.AuthGroup, pk=pk)
    user_choices = AuthUser.services.get_user_choices()

    selected_user_ids = list(
        AuthUser.objects.filter(groups=group).values_list('id', flat=True).distinct()
    )

    if request.method == 'POST':
        form = forms.GroupUserForm(data=request.POST)

        if form.is_valid():
            user_list = form.cleaned_data.get('users')
            set_group_users(group, user_list)

            group.add_activity(
                user=request.user,
                verb='added',
                information=(
                    f'{request.user.get_full_name()} added {len(user_list)} users to '
                    f'the group "{group.name}".'
                ),
            )

            return_url = reverse('django_spire:auth:group:page:detail', kwargs={'pk': pk})
            return HttpResponseRedirect(return_url)

        show_form_errors(request, form)

    form = forms.GroupUserForm()

    nav = AuthGroupNavigation()
    nav.page_title = 'Group'
    nav.page_description = 'Edit Users'
    nav.breadcrumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
    nav.breadcrumbs.add_model_instance_breadcrumb(
        group, url='django_spire:auth:group:page:detail', url_kwargs={'pk': group.pk}
    )
    nav.breadcrumbs.add_breadcrumb('Edit Users')

    context = nav.as_context()
    context['form'] = form
    context['group'] = group
    context['user_choices'] = user_choices
    context['selected_user_ids'] = selected_user_ids
    return TemplateResponse(
        request, context=context, template='django_spire/auth/group/page/group_user_form_page.html'
    )


@permission_required('django_spire_auth_group.delete_authgroup')
def delete_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    group = get_object_or_404(models.AuthGroup, pk=pk)
    return_url = reverse('django_spire:auth:group:page:list')

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=group)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                group.delete()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=group)

    nav = AuthGroupNavigation()
    nav.page_title = 'Delete Group'
    nav.breadcrumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
    nav.breadcrumbs.add_model_instance_breadcrumb(
        group, url='django_spire:auth:group:page:detail', url_kwargs={'pk': group.pk}
    )
    nav.breadcrumbs.add_breadcrumb('Delete')

    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {group}'
    context['form_description'] = f'Are you sure you would like to delete group "{group}"?'
    return TemplateResponse(
        request, context=context, template='django_spire/page/delete_confirmation_form_page.html'
    )


@permission_required('django_spire_auth_group.delete_authgroup')
def group_remove_user_form_view(
    request: WSGIRequest, group_pk: int, pk: int
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
                information=(
                    f'{request.user.get_full_name()} removed {user.get_full_name()} '
                    f'from the group "{group.name}".'
                ),
            )

            return HttpResponseRedirect(
                reverse('django_spire:auth:group:page:detail', kwargs={'pk': group_pk})
            )

    form = DeleteConfirmationForm(request.GET, obj=user)

    nav = AuthGroupNavigation()
    nav.page_title = 'Group'
    nav.page_description = f'Remove {user.get_full_name()} from'
    nav.breadcrumbs.add_breadcrumb('Groups', reverse('django_spire:auth:group:page:list'))
    nav.breadcrumbs.add_model_instance_breadcrumb(
        group, url='django_spire:auth:group:page:detail', url_kwargs={'pk': group.pk}
    )
    nav.breadcrumbs.add_breadcrumb(user.get_full_name())
    nav.breadcrumbs.add_breadcrumb('Remove')

    context = nav.as_context()
    context['form'] = form
    return TemplateResponse(
        request, context=context, template='django_spire/page/delete_confirmation_form_page.html'
    )
