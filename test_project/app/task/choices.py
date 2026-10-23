from django.db.models import TextChoices


class TaskOrderingChoices(TextChoices):
    NAME = 'name', 'Name'
    NAME_DESCENDING = '-name', 'Name, descending'
    STATUS = 'status', 'Status'
    NEWEST_FIRST = '-created_datetime', 'Newest first'


class TaskStatusChoices(TextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'inp', 'In Progress'
    DONE = 'com', 'Complete'
    CANCELLED = 'can', 'Cancelled'


class TaskUserRoleChoices(TextChoices):
    LEADER = 'lea', 'Leader'
    SUPPORT = 'sup', 'Support'
    FOLLOWER = 'fol', 'Follower'
