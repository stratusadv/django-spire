from django.urls import include, path

app_name = 'entry'

urlpatterns = [
    path('version/', include('django_spire.knowledge.entry.version.urls', namespace='version')),

    path('form/', include('django_spire.knowledge.entry.urls.form_urls', namespace='form')),
    path('json/', include('django_spire.knowledge.entry.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.knowledge.entry.urls.page_urls', namespace='page')),
    path('template/', include('django_spire.knowledge.entry.urls.template_urls', namespace='template')),
]
