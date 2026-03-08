from __future__ import annotations

from django.urls import path

from django_spire.api.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.access_create_form_view, name='create'),
]
