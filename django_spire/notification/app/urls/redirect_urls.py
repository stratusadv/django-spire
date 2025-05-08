from django.urls import path

from django_spire.notification.app.views import redirect_views


app_name = 'django_spire_notification'

urlpatterns = [
    path(
        "<int:pk>/delete/notification/ajax/",
        redirect_views.delete_notification_json_view,
        name="delete",
    )
]
