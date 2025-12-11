from __future__ import annotations

from django.urls import include, path

from django_spire.knowledge.collection import views


app_name = 'collection'

urlpatterns = [
    path('page/', include('django_spire.knowledge.collection.urls.page_urls', namespace='page')),
    path('json/', include('django_spire.knowledge.collection.urls.json_urls', namespace='json')),
    path('form/', include('django_spire.knowledge.collection.urls.form_urls', namespace='form')),
]
