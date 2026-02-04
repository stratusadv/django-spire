from __future__ import annotations

from django.urls.conf import include, path


app_name = 'domain'

urlpatterns = [
    path('page/', include('django_spire.metric.domain.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.domain.urls.form_urls', namespace='form')),
    path('template/', include('django_spire.metric.domain.urls.template_urls', namespace='template')),
]
