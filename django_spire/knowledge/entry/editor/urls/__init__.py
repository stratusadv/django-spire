from django.urls import include, path

app_name = 'editor'

urlpatterns = [
    path('page/', include('django_spire.knowledge.entry.editor.urls.page_urls', namespace='page')),
]
