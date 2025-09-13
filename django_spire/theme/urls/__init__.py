from django.urls.conf import path, include


app_name = 'theme'

urlpatterns = [
    path('ajax/', include('django_spire.theme.urls.ajax_urls', namespace='ajax')),
    path('page/', include('django_spire.theme.urls.page_urls', namespace='page')),
]
