from __future__ import annotations

from django.urls import include, path


app_name = 'sync'

urlpatterns = [
    path('page/', include('test_project.apps.sync.urls.page_urls', namespace='page')),
    path('form/', include('test_project.apps.sync.urls.form_urls', namespace='form')),
]
