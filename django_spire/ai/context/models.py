from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from django_spire.ai.context import querysets
from django_spire.ai.context.choices import PersonRoleChoices
from django_spire.auth.user.models import AuthUser
from django_spire.history.mixins import HistoryModelMixin


class Organization(HistoryModelMixin):
    name = models.CharField(max_length=255, default='')
    legal_name = models.CharField(max_length=255, default='')
    description = models.TextField(default='')
    sector = models.CharField(max_length=255, default='')
    sub_sector = models.CharField(max_length=255, default='')
    website = models.URLField(max_length=255, default='')
    street_address = models.CharField(max_length=255, default='')
    unit_number = models.CharField(max_length=32, default='')
    city = models.CharField(max_length=255, default='')
    province = models.CharField(max_length=255, default='')
    postal_code = models.CharField(max_length=16, default='')
    country = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=255, default='')
    email = models.EmailField(max_length=255, default='')

    objects = querysets.OrganizationQuerySet.as_manager()

    def save(self, *args, **kwargs) -> None:
        if self.pk is None and self.__class__.objects.exists():
            message = 'Only one AI Organization Context is allowed'
            raise ValidationError(message)

        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'django_spire_ai_context_organization'
        verbose_name = 'Organization Context'
        verbose_name_plural = 'Organization Context'


class Person(HistoryModelMixin):
    is_internal_to_organization = models.BooleanField(default=True)
    user = models.ForeignKey(
        AuthUser,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='ai_context_people',
        related_query_name='ai_context_person',
    )
    role = models.CharField(
        max_length=16, choices=PersonRoleChoices, default=PersonRoleChoices.ADMIN
    )
    role_details = models.TextField(default='')
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=255, default='')
    email = models.EmailField(max_length=255, default='')

    objects = querysets.PeopleQuerySet.as_manager()

    class Meta:
        db_table = 'django_spire_ai_context_person'
        verbose_name = 'Person Context'
        verbose_name_plural = 'People Context'
