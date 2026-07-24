from __future__ import annotations

from django.urls import path

from django_spire.metric.domain.views import form_views

app_name = 'form'

urlpatterns = [
    path('<int:pk>/form/', form_views.form_view, name='form'),
    path('<int:pk>/delete/', form_views.delete_form_view, name='delete'),
    path(
        'subdomain/<int:domain_pk>/<int:pk>/form/',
        form_views.subdomain_form_view,
        name='subdomain_form',
    ),
    path(
        'subdomain/<int:domain_pk>/<int:pk>/delete/',
        form_views.delete_subdomain_form_view,
        name='delete_subdomain',
    ),
]
