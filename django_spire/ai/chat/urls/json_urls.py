from django.urls import path

from django_spire.ai.chat.views import json_views


app_name = 'json'

urlpatterns = [
    path('<int:pk>/delete', json_views.delete_chat_view, name='delete'),
    path('<int:pk>/rename', json_views.rename_chat_view, name='rename'),
    path('workflow_process', json_views.chat_workflow_process_view, name='workflow_process'),
]
