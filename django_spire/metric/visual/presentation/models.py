from __future__ import annotations

from django.db import models, transaction

from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.utils import soft_delete_queryset

from django_spire.metric.visual.presentation import querysets
from django_spire.metric.visual.presentation.services.service import (
    PresentationService,
    SlideSectionService,
    SlideService,
)


class Presentation(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    objects = querysets.PresentationQuerySet().as_manager()
    services = PresentationService()

    def __str__(self) -> str:
        return self.name

    def set_deleted(self) -> None:
        with transaction.atomic():
            super().set_deleted()
            slide_pks = soft_delete_queryset(self.slides.all())
            soft_delete_queryset(SlideSection.objects.filter(slide_id__in=slide_pks))

    class Meta:
        verbose_name = 'Presentation'
        verbose_name_plural = 'Presentations'
        db_table = 'django_spire_metric_visual_presentation'


class Slide(HistoryModelMixin, ActivityMixin):
    presentation = models.ForeignKey(
        Presentation, on_delete=models.CASCADE, related_name='slides', related_query_name='slide'
    )
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField(default=0)

    objects = querysets.SlideQuerySet().as_manager()
    services = SlideService()

    def __str__(self) -> str:
        return self.name

    def set_deleted(self) -> None:
        with transaction.atomic():
            super().set_deleted()
            soft_delete_queryset(self.sections.all())

    class Meta:
        verbose_name = 'Slide'
        verbose_name_plural = 'Slides'
        db_table = 'django_spire_metric_visual_slide'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=('presentation', 'order'), name='unique_presentation_slide_order'
            )
        ]


class SlideSection(HistoryModelMixin, ActivityMixin):
    slide = models.ForeignKey(
        Slide, on_delete=models.CASCADE, related_name='sections', related_query_name='section'
    )
    visual = models.ForeignKey(
        'django_spire_metric_visual.Visual',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='slide_sections',
        related_query_name='slide_section',
    )
    row = models.PositiveSmallIntegerField(default=0)
    col = models.PositiveSmallIntegerField(default=0)

    objects = querysets.SlideSectionQuerySet().as_manager()
    services = SlideSectionService()

    def __str__(self) -> str:
        if self.visual_id:
            return f'{self.slide} - {self.visual}'

        return f'{self.slide} - Empty'

    class Meta:
        verbose_name = 'Slide Section'
        verbose_name_plural = 'Slide Sections'
        db_table = 'django_spire_metric_visual_slide_section'
        ordering = ('row', 'col')
