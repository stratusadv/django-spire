from django.urls import include, path

app_name = 'sms'


urlpatterns = [
    path('template/', include('django_spire.notification.sms.urls.template_urls', namespace='template')),
]
