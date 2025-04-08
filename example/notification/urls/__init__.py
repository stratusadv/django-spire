from django.urls import include, path

app_name = 'example_notification'

urlpatterns = [
    path('ajax/', include('example.notification.urls.ajax', namespace='ajax')),
    path('form/', include('example.notification.urls.form', namespace='form')),
    path('page/', include('example.notification.urls.page', namespace='page')),
]
