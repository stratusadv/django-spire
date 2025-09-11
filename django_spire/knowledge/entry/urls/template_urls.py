from django.urls import path

from django_spire.knowledge.entry.views import template_views

app_name = 'template'

urlpatterns = [
    path('files/<int:collection_pk>', template_views.file_list_view, name='file_list'),
]
