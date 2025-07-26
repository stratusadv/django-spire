from django.urls import path

from django_spire.knowledge.entry.views import json_views

app_name = 'json'

urlpatterns = [
    path(
        '<int:pk>/create_blank_block/',
        json_views.create_blank_block_view,
        name='create_blank_block',
    ),
    path(
        '<int:pk>/delete_block/',
        json_views.delete_block_view,
        name='delete_block',
    ),
]
