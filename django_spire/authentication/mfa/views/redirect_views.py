from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_spire.authentication.mfa.utils import get_or_generate_user_mfa_code


def mfa_notification_redirect_view(request):
    mfa_code = get_or_generate_user_mfa_code(request.user)

    if request.GET.get('resend', False):
        mfa_code.set_expired()
        mfa_code = get_or_generate_user_mfa_code(request.user)

    mfa_code.send_notification()
    messages.info(request, 'A authentication code has been sent to your email.')

    return HttpResponseRedirect(reverse('authentication:mfa:page:form'))
