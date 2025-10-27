from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from django_spire.ai.context import querysets
from django_spire.ai.context.choices import PeopleRoleChoices
from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin


class Organization(HistoryModelMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    sub_sector = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    unit_number = models.CharField(max_length=32, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=16, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    objects = querysets.OrganizationQuerySet.as_manager()

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
    is_internal_to_organization = models.BooleanField(default=True)
    user = models.ForeignKey(
        AuthUser,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ai_context_people',
        related_query_name='ai_context_people'
    )
    role = models.CharField(max_length=16, choices=PeopleRoleChoices, default=PeopleRoleChoices.ADMIN)
    role_details = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    objects = querysets.PeopleQuerySet.as_manager()

    class Meta:
        db_table = 'django_spire_ai_context_peopl'
        verbose_name = 'People Context'
        verbose_name_plural = 'People Context'

