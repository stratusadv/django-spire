from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import Group, User


class AiInteraction(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    user_email = models.EmailField(blank=True, null=True)
    user_first_name = models.CharField(max_length=100, blank=True, null=True)
    user_last_name = models.CharField(max_length=100, blank=True, null=True)

    module_name = models.TextField()
    callable_name = models.TextField()

    interaction = models.JSONField(blank=True, null=True)

    was_successful = models.BooleanField(default=True)
    exception = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)

    created_datetime = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if self.user:
            if self.user_email is None:
                self.user_email = self.user.email
            if self.user_first_name is None:
                self.user_first_name = self.user.first_name
            if self.user_last_name is None:
                self.user_last_name = self.user.last_name

        super().save(*args, **kwargs)



