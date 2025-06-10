from django.urls import path

from django_spire.notification.sms.views import template_views


app_name = 'django_spire_notification'

urlpatterns = [
    path('<uuid:external_access_key>/temporary_media/',
         template_views.temporary_media_view,
         name='temporary_media')
]
