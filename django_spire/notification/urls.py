from django.urls import include, path


app_name = 'notification'

urlpatterns = [
    path('app/', include('django_spire.notification.app.urls', namespace='app')),
    path('sms/', include('django_spire.notification.sms.urls', namespace='sms')),
]
