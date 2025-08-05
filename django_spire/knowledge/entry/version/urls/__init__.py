from django.urls import include, path

app_name = 'version'

urlpatterns = [
    path('block/', include('django_spire.knowledge.entry.version.block.urls', namespace='block')),

    path('form/', include('django_spire.knowledge.entry.version.urls.form_urls', namespace='form')),
    path('json/', include('django_spire.knowledge.entry.version.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.knowledge.entry.version.urls.page_urls', namespace='page')),
]
