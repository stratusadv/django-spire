from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.signage.views import form_views

app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path('link/create/', form_views.create_link_view, name='create_link'),
    path('link/<int:pk>/update/', form_views.update_link_view, name='update_link'),
    path('link/<int:pk>/delete/', form_views.delete_link_view, name='delete_link'),
]
