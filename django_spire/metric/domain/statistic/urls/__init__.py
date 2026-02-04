from __future__ import annotations

from django.urls.conf import include, path


app_name = 'statistic'

urlpatterns = [
    path('page/', include('django_spire.metric.domain.statistic.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.domain.statistic.urls.form_urls', namespace='form')),
    path('template/', include('django_spire.metric.domain.statistic.urls.template_urls', namespace='template')),
]
