from django.urls import path

from django_spire.notification.app.views import page


app_name = 'spire_notification'

urlpatterns = [
    path('spire/notification/list/',
         view=page.app_notification_list_view,
         name='list'
    )
]
