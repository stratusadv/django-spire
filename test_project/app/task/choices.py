from django.db.models import TextChoices


class TaskStatusChoices(TextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'inp', 'In Progress'
    DONE = 'com', 'Complete'
    CANCELLED = 'can', 'Cancelled'


class TaskUserRoleChoices(TextChoices):
    LEADER = 'lea', 'Leader'
    SUPPORT = 'sup', 'Support'
    FOLLOWER = 'fol', 'Follower'
