from django.db.models import TextChoices


class PriorityChoices(TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'med', 'Medium'
    HIGH = 'high', 'High'
