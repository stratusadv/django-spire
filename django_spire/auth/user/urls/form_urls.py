from __future__ import annotations

from django.urls import path

from django_spire.auth.user.views import form_views


app_name = 'form'

urlpatterns = [
    path('register/user/', form_views.register_form_view, name='register'),
    path('user/<int:pk>/form', form_views.form_view, name='update'),
    path('user/<int:pk>/group/form/', form_views.group_form_view, name='group_form'),
]
