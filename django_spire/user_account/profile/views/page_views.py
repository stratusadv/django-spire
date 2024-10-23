from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.core.breadcrumbs import Breadcrumbs
from django_spire.core.forms import DeleteConfirmationForm, ConfirmationForm
from django_spire.core.pagination.pagination import paginate_list
from django_spire.core.redirect import safe_redirect_url
from django_spire.history.utils import add_form_activity
from django_spire.user_account import forms
from django_spire.permission.models import PortalUser
from django_spire.permission.decorators import permission_required
from django_spire.permission.permissions import generate_group_perm_data, generate_user_perm_data
from django_spire.core.views import portal_views
from django_glue.glue import glue_model
from django_glue.utils import serialize_to_json


@permission_required('permission.view_portaluser')
def user_detail_page_view(request, pk):
    user = get_object_or_404(PortalUser, pk=pk)
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
        template='user_account/page/user_detail_page.html'
    )


@permission_required('permission.view_portaluser')
def user_list_page_view(request):
    user_list = PortalUser.objects.all()

    context_data = {
        'user_list': paginate_list(user_list, page_number=request.GET.get('page', 1))
    }

    return portal_views.list_view(
        request,
        context_data=context_data,
        model=PortalUser,
        template='user_account/page/user_list_page.html'
    )


@permission_required('permission.change_portaluser')
def user_form_page_view(request, pk):
    portal_user = get_object_or_404(PortalUser, pk=pk)
    glue_model(request, 'portal_user', portal_user, 'view')

    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=portal_user)
        if form.is_valid():
            portal_user = form.save()
            add_form_activity(portal_user, pk, request.user)
            return HttpResponseRedirect(reverse('user_account:profile:page:list'))
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
        template='user_account/page/user_form_page.html'
    )


@permission_required('permission.delete_portaluser')
def user_status_form_page_view(request, pk):
    user = get_object_or_404(PortalUser, pk=pk)

    form_class = DeleteConfirmationForm if user.is_active else ConfirmationForm

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():

            user.is_active = not user.is_active
            toggle_verb = 'activated' if user.is_active else 'deactivated'
            user.save()
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
