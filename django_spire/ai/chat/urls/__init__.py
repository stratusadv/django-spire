from django.urls import include, path

app_name = 'chat'

urlpatterns = [
    path('ajax/', include('example.notification.urls.ajax', namespace='ajax')),
]
