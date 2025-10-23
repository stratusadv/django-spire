from django.urls import path

from django_spire.knowledge.entry.version.views import json_views


app_name = 'json'


urlpatterns = [
    path(
        '<int:pk>/update_blocks/',

        json_views.update_blocks_view,
        name='update_blocks',
    ),
]
