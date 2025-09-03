from django.urls import path

from test_project.apps.ordering.views import json_views


app_name = 'json'

urlpatterns = [
    path('<int:pk>/<int:order>/reorder', json_views.reorder_json_view, name='reorder'),
]
