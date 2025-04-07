# Notification Factory Guide

### 👀 Overview 
The Notification Factory facilitates the creation of notifications by abstracting away the repetitive task of setting up notification data. This factory follows the `Factory Method` pattern, allowing developers to create notifications in a uniform manner across their application.   

#### Example 
```python
from django_spire.notification.factories import NotificationFactory

inventory_request = get_object_or_404(InventoryRequest, pk=1)

nf = NotificationFactory(
    title="New Inventory Item Request",
    body="A new inventory item request is pending approval.",
    url="https://example.com"
)

nf.create_email_notification('example@example.com')
nf.create_app_notification(model_object=inventory_request, user=request.user)

```
### 🖌️ Customization 

The Notification Factory can be extended or customized to meet specific needs. Developers can override methods in the `BaseNotificationFactory` class to add custom logic for creating notifications tailored to their application's requirements. 
#### Example

```python
class CustomNotificationFactory(BaseNotificationFactory):
    def create_email_notification(self, email: str) -> EmailNotification:
        notification = self.create_notification(NotificationTypeChoices.EMAIL)
        # Additional custom logic

        return EmailNotification.objects.create(
            notification=notification,
            subject=self.title,
            email=email
        )
```

## Source

::: django_spire.notification.factories.BaseNotificationFactory

::: django_spire.notification.factories.NotificationFactory
