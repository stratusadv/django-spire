from django.urls import path

from django_spire.knowledge.entry.views import json_views

app_name = 'json'

urlpatterns = [
    path('reorder/', json_views.reorder_view, name='reorder'),
    path('update/files/', json_views.update_files_view, name='update_files'),
]
