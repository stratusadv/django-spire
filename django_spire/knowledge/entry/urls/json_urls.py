from django.urls import path

from django_spire.knowledge.entry.views import json_views

app_name = 'json'

urlpatterns = [
    path('update/files/', json_views.update_files_view, name='update_files'),
]
