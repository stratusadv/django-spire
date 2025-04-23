from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.formats import localize
from django.utils.timezone import now

from django_spire.ai.mixins import AiUsageMixin


class AiUsage(AiUsageMixin):
    recorded_date = models.DateField(default=now)

    def __str__(self):
        return f'"{self.recorded_date}" ai usage'

    class Meta:
        db_table = 'django_spire_ai_usage'
        verbose_name = 'AI Usage'
        verbose_name_plural = 'AI Usage'


class AiInteraction(AiUsageMixin):
    ai_usage = models.ForeignKey(
        AiUsage,
        on_delete=models.CASCADE,
        related_name='interactions',
        related_query_name='interaction',
    )

    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ai_interactions',
        related_query_name='ai_interaction',
    )

    actor = models.CharField(max_length=100)
    user_email = models.EmailField(blank=True, null=True)
    user_first_name = models.CharField(max_length=100, blank=True, null=True)
    user_last_name = models.CharField(max_length=100, blank=True, null=True)

    module_name = models.TextField()
    callable_name = models.TextField()

    exception = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)

    created_datetime = models.DateTimeField(default=now)

    interaction = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'"{self.actor}" interaction on "{localize(self.created_datetime)}"'

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
        db_table = 'django_spire_ai_interaction'
        verbose_name = 'AI Interaction'
        verbose_name_plural = 'AI Interactions'
