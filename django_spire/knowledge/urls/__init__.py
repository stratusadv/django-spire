from django.urls import include, path

app_name = 'knowledge'

urlpatterns = [
    path('collection/', include('django_spire.knowledge.collection.urls', namespace='collection')),
    path('entry/', include('django_spire.knowledge.entry.urls', namespace='entry')),
]
