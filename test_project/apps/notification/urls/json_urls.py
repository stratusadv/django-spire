from django.urls import path

from test_project.apps.notification.views import json_views

app_name = 'json'

urlpatterns = [
    path('<int:pk>/process/', json_views.process_json_view, name='process')
]
