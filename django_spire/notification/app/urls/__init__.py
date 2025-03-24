from django.urls import include, path



app_name = 'spire_notification'


urlpatterns = [
    path('ajax/', include('django_spire.notification.app.urls.ajax', namespace='ajax')),
    path('form/', include('django_spire.notification.app.urls.form', namespace='form')),
    path('page/', include('django_spire.notification.app.urls.page', namespace='page')),
]
