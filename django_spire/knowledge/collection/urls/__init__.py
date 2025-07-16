from django.urls import include, path

from django_spire.knowledge.collection import views

app_name = 'collection'

urlpatterns = [
    path('page/', include('django_spire.knowledge.collection.urls.page_urls', namespace='page')),
]
