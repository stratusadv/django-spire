from django_spire.notification.models import Notification


def process_notifications():
    for notification in Notification.objects.filter(is_sent=False):
        notification.send()

    return 'Successfully Completed'
