from django.db import models

from django_spire.notification.models import Notification

class SmsNotification(models.Model):
    notification = models.ForeignKey(Notification, editable=False, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=11, blank=True)

    def __str__(self):
        return f'{self.notification.title} - {self.email}'
