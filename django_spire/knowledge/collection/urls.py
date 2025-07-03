from django.urls import include, path

from django_spire.knowledge.collection import views

app_name = 'collection'

urlpatterns = [
    path(
        'list/',
        views.collection_list_view,
        name='list'
    )
]
