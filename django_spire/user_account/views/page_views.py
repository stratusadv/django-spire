from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.breadcrumb import Breadcrumbs
from django_spire.form import show_form_errors
from django_spire.views import portal_views
from django_spire.history.utils import add_form_activity
from django_spire.permission.models import PortalUser
from django_spire.user_account import forms

from django_glue.glue import glue_model


def register_user_form_view(request):
    # Is this the best way to initialize a null object in glue?
    glue_model(request, 'portal_user', PortalUser(), 'view')

    if request.method == 'POST':
        user_form = forms.RegisterUserForm(request.POST)

        # Checks to see if all forms are valid.
        if user_form.is_valid():
            user = user_form.save()

            # Add form activity. This needs to be improved.
            add_form_activity(user, 0, request.user)

            return HttpResponseRedirect(reverse('user_account:profile:page:list'))

        show_form_errors(request, user_form)
    else:
        # If the form has an initial it will override the defaults.
        user_form = forms.RegisterUserForm()

    context_data = {
        # Todo: Function that takes in all of the forms and dumps the data here?
        'user_form_data': json.dumps(user_form.data, cls=DjangoJSONEncoder),
    }

    crumbs = Breadcrumbs()
    crumbs.add_breadcrumb(name='Users', href=reverse('user_account:profile:page:list'))
    crumbs.add_breadcrumb(name='Register New User')

    return portal_views.template_view(
        request,
        context_data=context_data,
        page_title='Register',
        page_description='New User',
        breadcrumbs=crumbs,
        template='spire/user_account/page/register_user_form_page.html'
    )

