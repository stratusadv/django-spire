from django.db import models


class ApiPermissionChoices(models.IntegerChoices):
    """
    Choices for API access levels are required to be in order of least to most restrictive.
    """
    VIEW = 1, 'View'
    ADD = 2, 'Add'
    CHANGE = 3, 'Change'
    DELETE = 4, 'Delete'
