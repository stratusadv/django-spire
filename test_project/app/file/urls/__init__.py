from django.urls import include, path


app_name = 'file'

urlpatterns = [
    path('form/', include('test_project.apps.file.urls.form_urls', namespace='form')),
    path('json/', include('test_project.apps.file.urls.json_urls', namespace='json')),
    path('page/', include('test_project.apps.file.urls.page_urls', namespace='page')),
]
