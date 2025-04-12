from django.urls import path

from django_spire.ai.chat.views import json_views


app_name = 'json'

urlpatterns = [
    path('workflow_process', json_views.chat_workflow_process_json_view, name='workflow_process'),
]
