from django.urls.conf import path, include


app_name = 'theme'

urlpatterns = [
    path('json/', include('django_spire.theme.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.theme.urls.page_urls', namespace='page')),
]
