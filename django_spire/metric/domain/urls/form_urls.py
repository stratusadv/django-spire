from __future__ import annotations

from django.urls import path

from django_spire.metric.domain.views import form_views

app_name = 'form'

urlpatterns = [

    path('<int:pk>/form/', form_views.form_view, name='form'),

    # path('create/', form_views.create_view, name='create'),
    # path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_form_view, name='delete'),
    path(
        'subdomain/<int:domain_pk>/create/',
        form_views.create_subdomain_view,
        name='create_subdomain',
    ),
    path(
        'subdomain/<int:domain_pk>/<int:pk>/update/',
        form_views.update_subdomain_view,
        name='update_subdomain',
    ),
    path(
        'subdomain/<int:domain_pk>/<int:pk>/delete/',
        form_views.delete_subdomain_form_view,
        name='delete_subdomain',
    ),
]
