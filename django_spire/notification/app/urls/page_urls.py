from django.urls import path

from django_spire.notification.app.views import page_views


app_name = 'django_spire_notification'

urlpatterns = [
    path('django_spire/notification/list/',
         view=page_views.app_notification_list_view,
         name='list'
    )
]
