from django.urls import path, include


app_name = 'notification'

urlpatterns = [
    # TODO: Change to app
    path('app/', include('django_spire.notification.app.urls', namespace='group')),
]
