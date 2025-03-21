from django.db import models

from django_spire.notification.models import Notification

class EmailNotification(models.Model):
    notification = models.ForeignKey(Notification, editable=False, on_delete=models.CASCADE)
    subject = models.CharField(max_length=128)
    email = models.EmailField()

    def __str__(self):
        return f'{self.notification.title} - {self.email}'

