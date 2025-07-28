from django.urls import include, path

app_name = 'entry'

urlpatterns = [
    path('block/', include('django_spire.knowledge.entry.block.urls', namespace='block')),
    path('editor/', include('django_spire.knowledge.entry.editor.urls', namespace='editor')),

    path('json/', include('django_spire.knowledge.entry.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.knowledge.entry.urls.page_urls', namespace='page')),
]
