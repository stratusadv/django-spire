from __future__ import annotations

from django.urls import path

from django_spire.metric.domain.statistic.views import form_views

app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('<int:pk>/delete/', form_views.delete_form_view, name='delete'),
    path('group/create/', form_views.group_create_view, name='group_create'),
    path('group/<int:pk>/update/', form_views.group_update_view, name='group_update'),
    path('group/<int:pk>/delete/', form_views.group_delete_form_view, name='group_delete'),
]
