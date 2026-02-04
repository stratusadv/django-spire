from __future__ import annotations

from django.urls.conf import include, path


app_name = 'visual'

urlpatterns = [
    path('page/', include('django_spire.metric.visual.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.visual.urls.form_urls', namespace='form')),
    path('template/', include('django_spire.metric.visual.urls.template_urls', namespace='template')),
]
