from django.urls import include, path

app_name = 'test_project_notification'

urlpatterns = [
    path('form/', include('test_project.apps.notification.urls.form_urls', namespace='form')),
    path('json/', include('test_project.apps.notification.urls.json_urls', namespace='json')),
    path('page/', include('test_project.apps.notification.urls.page_urls', namespace='page')),
]
