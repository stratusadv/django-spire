from django.urls import path

from django_spire.knowledge.collection.views import json_views


app_name = 'json'

urlpatterns = [
    path('<int:pk>/reorder', json_views.reorder_view, name='reorder'),
]
