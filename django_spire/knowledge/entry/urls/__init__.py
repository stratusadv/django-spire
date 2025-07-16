from django.urls import include, path

app_name = 'entry'

urlpatterns = [
    path('block/', include('django_spire.knowledge.entry.block.urls', namespace='block')),
    path('editor/', include('django_spire.knowledge.entry.editor.urls', namespace='editor')),
]
