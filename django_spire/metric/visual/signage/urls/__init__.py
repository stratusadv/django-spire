from __future__ import annotations

from django.urls.conf import include, path


app_name = 'signage'

urlpatterns = [
    path('page/', include('django_spire.metric.visual.signage.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.visual.signage.urls.form_urls', namespace='form')),
    path('template/', include('django_spire.metric.visual.signage.urls.template_urls', namespace='template')),
]
