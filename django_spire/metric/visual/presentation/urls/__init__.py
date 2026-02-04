from __future__ import annotations

from django.urls.conf import include, path


app_name = 'presentation'

urlpatterns = [
    path('page/', include('django_spire.metric.visual.presentation.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.visual.presentation.urls.form_urls', namespace='form')),
    path('template/', include('django_spire.metric.visual.presentation.urls.template_urls', namespace='template')),
]
