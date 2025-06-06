from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from django_spire.contrib.form.utils import show_form_errors


class LoginView(auth_views.LoginView):
    template_name = 'django_spire/auth/page/login_page.html'

    def form_invalid(self, form):
        show_form_errors(self.request, form)
        return super().form_invalid(form)


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'django_spire/auth/page/password_change_page.html'
    success_url = reverse_lazy('django_spire:auth:admin:password_change_done')


class PasswordChangeDone(auth_views.PasswordChangeDoneView):
    template_name = 'django_spire/auth/page/password_change_done_page.html'


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = 'django_spire/auth/password_reset_email.html'
    success_url = reverse_lazy('django_spire:auth:admin:password_reset_done')
    template_name = 'django_spire/auth/page/password_reset_page.html'


class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = 'django_spire/auth/page/password_reset_complete_page.html'


class PasswordResetConfirmation(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('django_spire:auth:admin:password_reset_complete')
    template_name = 'django_spire/auth/page/password_reset_confirmation_page.html'


class PasswordResetDone(auth_views.PasswordResetDoneView):
    template_name = 'django_spire/auth/page/password_reset_done_page.html'


class PasswordResetKeyForm(auth_views.PasswordResetView):
    template_name = 'django_spire/auth/page/password_reset_key_form_page.html'


class PasswordResetKeyFormDone(auth_views.PasswordResetView):
    template_name = 'django_spire/auth/page/password_reset_key_done_page.html'


class PasswordSetForm(auth_views.PasswordResetView):
    template_name = 'django_spire/auth/page/password_set_form_page.html'
