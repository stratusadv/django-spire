from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from django_spire.ai.context.choices import PeopleRoleChoices
from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin


class Organization(HistoryModelMixin):
    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255)
    description = models.TextField()
    sector = models.CharField(max_length=255)
    sub_sector = models.CharField(max_length=255)
    website = models.URLField(max_length=255)
    street_address = models.CharField(max_length=255)
    unit_number = models.CharField(max_length=32)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=16)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.__class__.objects.exists():
                raise ValidationError('Only one AI Organization Context is allowed')

        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'django_spire_ai_context_organization'
        verbose_name = 'Organization Context'
        verbose_name_plural = 'Organization Context'


class People(HistoryModelMixin):
    user = models.ForeignKey(
        AuthUser,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ai_context_people',
        related_query_name='ai_context_people'
    )
    role = models.CharField(max_length=16, choices=PeopleRoleChoices, default=PeopleRoleChoices.ADMIN)
    role_details = models.TextField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    class Meta:
        db_table = 'django_spire_ai_context_peopl'
        verbose_name = 'People Context'
        verbose_name_plural = 'People Context'

