from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.formats import localize
from django.utils.timezone import now


class AiInteraction(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    actor = models.CharField(max_length=100)
    user_email = models.EmailField(blank=True, null=True)
    user_first_name = models.CharField(max_length=100, blank=True, null=True)
    user_last_name = models.CharField(max_length=100, blank=True, null=True)

    module_name = models.TextField()
    callable_name = models.TextField()

    was_successful = models.BooleanField(default=True)
    exception = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)

    created_datetime = models.DateTimeField(default=now)

    interaction = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'"{self.actor}" ai interaction with "{self.module_name}.{self.callable_name}" on "{localize(self.created_datetime)}"'

    def save(self, *args, **kwargs):
        if self.user:
            if self.actor is None:
                self.actor = self.user.get_full_name()
            if self.user_email is None:
                self.user_email = self.user.email
            if self.user_first_name is None:
                self.user_first_name = self.user.first_name
            if self.user_last_name is None:
                self.user_last_name = self.user.last_name

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'spire_ai_interaction'

