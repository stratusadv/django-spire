from django.urls import path

from django_spire.notification.app.views import ajax


app_name = 'spire_notification'

urlpatterns = [
    path('check/notification/ajax/',
         ajax.check_new_notifications_ajax_view,
         name='check_new_notifications')
]
