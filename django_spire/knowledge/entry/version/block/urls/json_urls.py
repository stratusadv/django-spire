from django.urls import path

from django_spire.knowledge.entry.version.block.views import json_views

app_name = 'json'

urlpatterns = [
    path('update_text/', json_views.update_text_view, name='update_text'),
]
