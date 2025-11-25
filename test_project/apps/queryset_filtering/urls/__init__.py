from django.urls import path, include

app_name = 'queryset_filtering'

urlpatterns = [
    path('page/', include('test_project.apps.queryset_filtering.urls.page_urls', namespace='page')),
    path('form/', include('test_project.apps.queryset_filtering.urls.form_urls', namespace='form')),
]
