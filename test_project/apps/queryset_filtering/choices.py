from django.db.models import TextChoices


class TaskStatusChoices(TextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'inp', 'In Progress'
    DONE = 'com', 'Complete'
    CANCELLED = 'can', 'Cancelled'

