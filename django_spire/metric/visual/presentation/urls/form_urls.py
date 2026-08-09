from __future__ import annotations

from django.urls import path

from django_spire.metric.visual.presentation.views import form_views

app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path('slide/create/', form_views.create_slide_view, name='create_slide'),
    path('slide/<int:pk>/update/', form_views.update_slide_view, name='update_slide'),
    path('slide/<int:pk>/delete/', form_views.delete_slide_view, name='delete_slide'),
    path('section/create/', form_views.create_section_view, name='create_section'),
    path('section/<int:pk>/update/', form_views.update_section_view, name='update_section'),
    path('section/<int:pk>/delete/', form_views.delete_section_view, name='delete_section'),
]
