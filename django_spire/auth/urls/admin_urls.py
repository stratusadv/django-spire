from django.urls import path

from django_spire.auth.views import admin_views


app_name = 'admin'

urlpatterns = [
    path('login/',
         admin_views.LoginView.as_view(),
         name='login'),
]


# Password Views
urlpatterns += [
    path('password/change/',
         admin_views.PasswordChangeView.as_view(),
         name='password_change'),

    path('password/change/done/',
         admin_views.PasswordChangeDone.as_view(),
         name='password_change_done'),

    path('password/reset/',
         admin_views.PasswordResetView.as_view(),
         name='password_reset'),

    path('password/reset/complete/',
         admin_views.PasswordResetComplete.as_view(),
         name='password_reset_complete'),

    path('password/reset/confirmation/<uidb64>/<token>/',
         admin_views.PasswordResetConfirmation.as_view(),
         name='password_reset_confirmation'),

    path('password/reset/done/',
         admin_views.PasswordResetDone.as_view(),
         name='password_reset_done'),

    path('password/reset/key/form/',
         admin_views.PasswordResetKeyForm.as_view(),
         name='password_reset_key_form'),

    path('password/reset/key/form/done/',
         admin_views.PasswordResetKeyFormDone.as_view(),
         name='password_reset_key_form_done'),

    path('password/reset/set/',
         admin_views.PasswordSetForm.as_view(),
         name='password_set_form'),
]
