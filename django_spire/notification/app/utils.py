from django_spire.notification.app.models import AppNotification

def get_app_notification_list_by_user_id(user_id: int) -> list[AppNotification]:
    return AppNotification.objects.filter(user_id=user_id)
