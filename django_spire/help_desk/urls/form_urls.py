from __future__ import annotations

from django.urls import path

from django_spire.help_desk.views import form_views


app_name = 'form'

urlpatterns = [
    path('<int:pk>/form/', form_views.form_view, name='form'),
    path('<int:pk>/delete/', form_views.ticket_delete_view, name='delete'),
]
