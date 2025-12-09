from __future__ import annotations

from django.urls import path

from django_spire.knowledge.collection.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.form_view, name='create'),
    path('<int:parent_pk>/create_with_parent/', form_views.form_view, name='create_with_parent'),
    path('<int:pk>/update/', form_views.form_view, name='update'),
]
