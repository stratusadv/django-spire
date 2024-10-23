from django_spire.core.notification.models import Notification


def process_notifications():
    for notification in Notification.objects.filter(is_sent=False):
        notification.send()
    return 'Successfully Completed'
