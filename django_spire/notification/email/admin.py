from django.contrib import admin

from django_spire.notification.email.models import EmailNotification

# Register your models here.
@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'notification', 'subject', 'email'
    )
