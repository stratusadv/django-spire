from django.urls.conf import path, include


app_name = 'ordering'

urlpatterns = [
    path('page/', include('test_project.apps.ordering.urls.page_urls', namespace='page')),
    path('json/', include('test_project.apps.ordering.urls.json_urls', namespace='json')),
    path('form/', include('test_project.apps.ordering.urls.form_urls', namespace='form')),
]
