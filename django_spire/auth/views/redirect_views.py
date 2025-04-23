from __future__ import annotations

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required()
def login_redirect_view(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('django_spire:auth:admin:login'))
    else:
        # MFA implementation if required
        # profile = request.user.profile
        #
        # if profile.requires_mfa():
        #     return HttpResponseRedirect(reverse('django_spire:auth:mfa:redirect:notification'))

        return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_SUCCESS_URL))


@login_required()
def logout_redirect_view(request, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('django_spire:auth:admin:login'))
