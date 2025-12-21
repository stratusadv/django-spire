from __future__ import annotations

from django.urls import include, path


app_name = 'app'

urlpatterns = [
    path('json/', include('django_spire.notification.app.urls.json_urls', namespace='json')),
    path('page/', include('django_spire.notification.app.urls.page_urls', namespace='page')),
    path('template/', include('django_spire.notification.app.urls.template_urls', namespace='template')),
]
