from django.db import models

class EventHistoryChoices(models.TextChoices):
    CREATED = 'crea', 'Created'
    UPDATED = 'upda', 'Updated'
    ACTIVE = 'acti', 'Active'
    INACTIVE = 'inac', 'Inactive'
    DELETED = 'dele', 'Deleted'
    UNDELETED = 'unde', 'Un-Deleted'
