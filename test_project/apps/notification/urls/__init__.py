from django.urls import include, path

app_name = 'test_project_notification'

urlpatterns = [
    path('json/', include('test_project.apps.notification.urls.json_views', namespace='json')),
    path('form/', include('test_project.apps.notification.urls.form_views', namespace='form')),
    path('page/', include('test_project.apps.notification.urls.page_views', namespace='page')),
]
