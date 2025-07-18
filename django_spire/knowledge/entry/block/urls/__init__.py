from django.urls import include, path

app_name = 'block'

urlpatterns = [
    path(
        'json/',
        include('django_spire.knowledge.entry.block.urls.json_urls', namespace='json')
    ),
]
