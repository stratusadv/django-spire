from django.urls import include, path

app_name = 'notification'

urlpatterns = [
    # path('ajax/', include('example.notification.urls.ajax', namespace='page')),
    path('form/', include('example.notification.urls.form', namespace='form')),
    path('page/', include('example.notification.urls.page', namespace='page')),
]
