import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.core.forms import show_form_errors
from django_spire.history.utils import add_form_activity
from django_spire.user_account import forms
from django_spire.permission.models import PortalUser
from django_spire.core.views import portal_views
from django_spire.core.breadcrumbs import Breadcrumbs
from django_glue.glue import glue_model


def register_user_form_view(request):
    # Is this the best way to initialize a null object in glue?
    glue_model(request, 'portal_user', PortalUser(), 'view')

    if request.method == 'POST':
        user_form = forms.RegisterUserForm(request.POST)

        if user_form.is_valid():  # Checks to see if all forms are valid.
            user = user_form.save()  # Save each form...
            add_form_activity(user, 0, request.user)  # Add form activity. This needs to be improved.
            return HttpResponseRedirect(reverse('user_account:profile:page:list'))  # Redirect to new view.
        else:
            show_form_errors(request, user_form)
    else:
        user_form = forms.RegisterUserForm()  # If the form has an initial it will override the defaults.

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
        template='user_account/page/register_user_form_page.html'
    )

