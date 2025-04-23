from django.urls import path, include


app_name = 'notification'

urlpatterns = [
    path('app/', include('django_spire.notification.app.urls', namespace='group')),
]
