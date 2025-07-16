from django.urls import path

from django_spire.knowledge.collection.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.collection_list_view, name='list'),
]
