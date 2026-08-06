from __future__ import annotations

from django.urls import path

from django_spire.auth.user.views import form_views


app_name = 'form'

urlpatterns = [
    path('user/<int:pk>/form/', form_views.form_view, name='form'),
    path('user/<int:pk>/group/form/', form_views.group_form_view, name='group_form'),
    path('user/<int:pk>/password/reset/', form_views.reset_password_view, name='reset_password'),
]
