from django.urls import include, path

app_name = 'test_project_notification'

urlpatterns = [
    path('ajax/', include('test_project.apps.notification.urls.ajax', namespace='ajax')),
    path('form/', include('test_project.apps.notification.urls.form', namespace='form')),
    path('page/', include('test_project.apps.notification.urls.page', namespace='page')),
]
