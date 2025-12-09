from django.urls import include, path


app_name = 'version'

urlpatterns = [
    path('json/', include('django_spire.knowledge.entry.version.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.knowledge.entry.version.urls.page_urls', namespace='page')),
    path('redirect/', include('django_spire.knowledge.entry.version.urls.redirect_urls', namespace='redirect')),
]
