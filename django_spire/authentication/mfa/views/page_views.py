from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.authentication.mfa.utils import get_or_generate_user_mfa_code
from django_spire.authentication.mfa import forms


def mfa_form_view(request):
    mfa_code = get_or_generate_user_mfa_code(request.user)
    profile = request.user.profile

    if request.method == 'POST':
        form = forms.MFAForm(mfa_code, request.POST)
        if form.is_valid():
            mfa_code.set_expired()
            profile.set_mfa_grace_period()
            return HttpResponseRedirect(reverse('home:home'))

        if 'mfa_code' in form.errors:
            messages.error(request, form.errors['mfa_code'][0])

    context_data = {
        'form': forms.MFAForm(mfa_code, initial=request.POST),
        'form_description': 'An authentication code has been sent to your email. Please enter it below to continue.',
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='authentication/mfa/mfa_form.html'
    )

