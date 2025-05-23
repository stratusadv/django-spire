from django.db import models


class HelpDeskTicketPurposeChoices(models.TextChoices):
    APP = ('app', 'App')
    COMPANY = ('comp', 'Company')


class HelpDeskTicketStatusChoices(models.TextChoices):
    READY = ('read', 'Ready')
    INPROGRESS = ('prog', 'In Progress')
    DONE = ('done', 'Done')


class HelpDeskTicketPriorityChoices(models.TextChoices):
    LOW = ('low', 'Low')
    MEDIUM = ('med', 'Medium')
    HIGH = ('high', 'High')
    URGENT = ('urge', 'Urgent')
