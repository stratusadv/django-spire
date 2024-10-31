from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class LoginView(auth_views.LoginView):
    template_name = 'user_account/authentication/page/login_page.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'user_account/authentication/page/password_change_page.html'
    success_url = reverse_lazy('user_account:authentication:admin:password_change_done')


class PasswordChangeDone(auth_views.PasswordChangeDoneView):
    template_name = 'user_account/authentication/page/password_change_done_page.html'


class PasswordResetView(auth_views.PasswordResetView):
    email_template_name = "authentication/password_reset_email.html"
    success_url = reverse_lazy('user_account:authentication:admin:password_reset_done')
    template_name = 'user_account/authentication/page/password_reset_page.html'


class PasswordResetComplete(auth_views.PasswordResetCompleteView):
    template_name = 'user_account/authentication/page/password_reset_complete_page.html'


class PasswordResetConfirmation(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('user_account:authentication:admin:password_reset_complete')
    template_name = 'user_account/authentication/page/password_reset_confirmation_page.html'


class PasswordResetDone(auth_views.PasswordResetDoneView):
    template_name = 'user_account/authentication/page/password_reset_done_page.html'


class PasswordResetKeyForm(auth_views.PasswordResetView):
    template_name = 'user_account/authentication/page/password_reset_key_form_page.html'


class PasswordResetKeyFormDone(auth_views.PasswordResetView):
    template_name = 'user_account/authentication/page/password_reset_key_done_page.html'


class PasswordSetForm(auth_views.PasswordResetView):
    template_name = 'user_account/authentication/page/password_set_form_page.html'
