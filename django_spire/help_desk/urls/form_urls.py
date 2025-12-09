from __future__ import annotations

from django.urls import path

from django_spire.help_desk.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.ticket_create_form_view, name='create'),
    path('<int:pk>/update/', form_views.ticket_update_form_view, name='update'),
]
