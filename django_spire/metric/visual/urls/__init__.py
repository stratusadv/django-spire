from __future__ import annotations

from django.urls.conf import include, path

app_name = 'visual'

urlpatterns = [
    path('page/', include('django_spire.metric.visual.urls.page_urls', namespace='page')),
    path('form/', include('django_spire.metric.visual.urls.form_urls', namespace='form')),
    path(
        'presentation/',
        include('django_spire.metric.visual.presentation.urls', namespace='presentation'),
    ),
    path('signage/', include('django_spire.metric.visual.signage.urls', namespace='signage')),
]
