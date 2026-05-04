from __future__ import annotations

from django.urls import path

from test_project.apps.sync.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/<str:model>/', form_views.create_form_view, name='create'),
    path('update/<str:model>/<int:pk>/', form_views.update_form_view, name='update'),
]
