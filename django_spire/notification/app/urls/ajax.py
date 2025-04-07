from django.urls import path

from django_spire.notification.app.views import ajax


app_name = 'spire_notification'

urlpatterns = [
    path('check/notification/ajax/',
         ajax.check_new_notifications_ajax_view,
         name='check_new'),

    path('set_viewed/notification/ajax/',
         ajax.set_notifications_as_viewed_ajax,
         name='set_viewed'),
]
