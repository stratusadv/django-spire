from django.urls import path

from django_spire.notification.app.views import template


app_name = 'spire_notification'

urlpatterns = [
    path('notficiation/dropdown/template/',
         template.notification_dropdown_template_view,
         name='notification_dropdown')
]
