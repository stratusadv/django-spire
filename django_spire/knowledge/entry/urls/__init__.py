from django.urls import include, path

app_name = 'entry'

urlpatterns = [
    path('version/', include('django_spire.knowledge.entry.version.urls', namespace='version')),

    path('form/', include('django_spire.knowledge.entry.urls.form_urls', namespace='form')),
    path('page/', include('django_spire.knowledge.entry.urls.page_urls', namespace='page')),
]
