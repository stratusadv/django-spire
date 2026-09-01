from __future__ import annotations

from uuid import uuid4

from django.db import models, transaction

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.utils import soft_delete_queryset

from django_spire.metric.visual.signage import querysets
from django_spire.metric.visual.signage.services.service import (
    SignagePresentationService,
    SignageService,
)


class Signage(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(default='')
    slide_display_seconds = models.PositiveSmallIntegerField(default=30)
    key = models.UUIDField(default=uuid4, unique=True, editable=False)

    # This M2M accessor does not filter soft-deleted through rows; use
    # SignageTransformationService.presentations()/presentation_links() instead.
    presentations = models.ManyToManyField(
        'django_spire_metric_visual_presentation.Presentation',
        through='SignagePresentation',
        through_fields=('signage', 'presentation'),
        related_name='signages',
        related_query_name='signage',
        blank=True,
    )

    objects = querysets.SignageQuerySet().as_manager()
    services = SignageService()

    def __str__(self) -> str:
        return self.name

    def set_deleted(self) -> None:
        with transaction.atomic():
            super().set_deleted()
            soft_delete_queryset(self.signage_presentations.all())

    class Meta:
        verbose_name = 'Signage'
        verbose_name_plural = 'Signages'
        db_table = 'django_spire_metric_visual_signage'


class SignagePresentation(HistoryModelMixin, ActivityMixin):
    signage = models.ForeignKey(
        Signage,
        on_delete=models.CASCADE,
        related_name='signage_presentations',
        related_query_name='signage_presentation',
    )
    presentation = models.ForeignKey(
        'django_spire_metric_visual_presentation.Presentation',
        on_delete=models.CASCADE,
        related_name='presentation_links',
        related_query_name='presentation_link',
    )
    order = models.PositiveSmallIntegerField(default=0)

    objects = querysets.SignagePresentationQuerySet().as_manager()
    services = SignagePresentationService()

    def __str__(self) -> str:
        return f'{self.signage} - {self.presentation}'

    class Meta:
        verbose_name = 'Signage Presentation'
        verbose_name_plural = 'Signage Presentations'
        db_table = 'django_spire_metric_visual_signage_presentation'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=('signage', 'order'), name='unique_signage_presentation_order'
            )
        ]
