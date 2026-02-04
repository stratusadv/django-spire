from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.signage.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_form_view, name='delete'),
    path('create/modal/', form_views.create_modal_view, name='create_modal'),
    path('<int:pk>/update/modal/', form_views.update_modal_view, name='update_modal'),
    path('<int:pk>/delete/modal/', form_views.delete_modal_view, name='delete_modal'),
]
