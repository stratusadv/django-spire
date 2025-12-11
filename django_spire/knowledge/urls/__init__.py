from __future__ import annotations

from django.urls import include, path


app_name = 'knowledge'

urlpatterns = [
    path('page/', include('django_spire.knowledge.urls.page_urls', namespace='page')),
    path('collection/', include('django_spire.knowledge.collection.urls', namespace='collection')),
    path('entry/', include('django_spire.knowledge.entry.urls', namespace='entry')),
]
