from __future__ import annotations

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required()
def login_redirect_view(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user_account:authentication:admin:login'))
    else:
        # MFA implementation if required
        # profile = request.user.profile
        #
        # if profile.requires_mfa():
        #     return HttpResponseRedirect(reverse('user_account:authentication:mfa:redirect:notification'))

        return HttpResponseRedirect(reverse('home:home'))


@login_required()
def logout_redirect_view(request, **kwargs):
    logout(request)
    return HttpResponseRedirect(reverse('user_account:authentication:admin:login'))
