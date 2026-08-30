from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.activity.mixins import ActivityMixin

from django_spire.metric.visual import querysets
from django_spire.metric.visual.choices import (
    VisualConditionOperatorChoices,
    VisualConditionStateChoices,
    VisualKindChoices,
)
from django_spire.metric.visual.services.service import (
    AreaChartVisualService,
    BarChartVisualService,
    GaugeChartVisualService,
    IndicatorVisualService,
    LineChartVisualService,
    PieChartVisualService,
    VisualConditionService,
    VisualReferenceService,
    VisualService,
)

if TYPE_CHECKING:
    from typing import Any


def kind_manager(kind: str) -> models.Manager:
    class VisualKindManager(models.Manager.from_queryset(querysets.VisualQuerySet)):
        def get_queryset(self) -> models.QuerySet:
            return super().get_queryset().filter(kind=kind)

    return VisualKindManager()


class Visual(HistoryModelMixin, ActivityMixin):
    name = models.CharField(max_length=255)
    description = models.TextField(default='')

    statistic = models.ForeignKey(
        'django_spire_metric_domain.Statistic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visuals',
        related_query_name='visual',
    )
    date = models.DateField(default=timezone.localdate)
    kind = models.CharField(
        max_length=20, choices=VisualKindChoices.choices, default=VisualKindChoices.INDICATOR
    )

    objects = querysets.VisualQuerySet().as_manager()
    services = VisualService()

    _kind_model_registry: dict[str, type[Visual]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        kind = getattr(cls, 'KIND', None)
        if kind is not None:
            cls._kind_model_registry[kind] = cls

    @property
    def is_chart(self) -> bool:
        return self.kind != VisualKindChoices.INDICATOR

    @classmethod
    def kind_model(cls, kind: str) -> type[Visual]:
        return cls._kind_model_registry.get(kind, cls)

    @classmethod
    def subclass_for(cls, obj: Visual) -> Visual:
        return cls.kind_model(obj.kind).objects.get(pk=obj.pk)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Visual'
        verbose_name_plural = 'Visuals'
        db_table = 'django_spire_metric_visual'


class IndicatorVisual(Visual):
    KIND = VisualKindChoices.INDICATOR
    objects = kind_manager(VisualKindChoices.INDICATOR)
    services = IndicatorVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Indicator Visual'
        verbose_name_plural = 'Indicator Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class LineChartVisual(Visual):
    KIND = VisualKindChoices.LINE
    objects = kind_manager(VisualKindChoices.LINE)
    services = LineChartVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Line Chart Visual'
        verbose_name_plural = 'Line Chart Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class BarChartVisual(Visual):
    KIND = VisualKindChoices.BAR
    objects = kind_manager(VisualKindChoices.BAR)
    services = BarChartVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Bar Chart Visual'
        verbose_name_plural = 'Bar Chart Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class AreaChartVisual(Visual):
    KIND = VisualKindChoices.AREA
    objects = kind_manager(VisualKindChoices.AREA)
    services = AreaChartVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Area Chart Visual'
        verbose_name_plural = 'Area Chart Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class PieChartVisual(Visual):
    KIND = VisualKindChoices.PIE
    objects = kind_manager(VisualKindChoices.PIE)
    services = PieChartVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Pie Chart Visual'
        verbose_name_plural = 'Pie Chart Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class GaugeChartVisual(Visual):
    KIND = VisualKindChoices.GAUGE
    objects = kind_manager(VisualKindChoices.GAUGE)
    services = GaugeChartVisualService()

    class Meta:
        proxy = True
        verbose_name = 'Gauge Chart Visual'
        verbose_name_plural = 'Gauge Chart Visuals'

    def save(self, *args, **kwargs) -> None:
        self.kind = self.KIND
        super().save(*args, **kwargs)


class VisualCondition(HistoryModelMixin, ActivityMixin):
    visual = models.ForeignKey(
        Visual, on_delete=models.CASCADE, related_name='conditions', related_query_name='condition'
    )

    state = models.CharField(
        max_length=10,
        choices=VisualConditionStateChoices.choices,
        default=VisualConditionStateChoices.GREEN,
    )
    operator = models.CharField(
        max_length=10,
        choices=VisualConditionOperatorChoices.choices,
        default=VisualConditionOperatorChoices.GT,
    )
    target = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    tolerance = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    order = models.PositiveSmallIntegerField(default=0)

    objects = querysets.VisualConditionQuerySet().as_manager()
    services = VisualConditionService()

    def matches(self, value: Decimal) -> bool:
        value = Decimal(value)

        comparisons: dict[str, bool] = {
            VisualConditionOperatorChoices.GT: value > self.target,
            VisualConditionOperatorChoices.GTE: value >= self.target,
            VisualConditionOperatorChoices.LT: value < self.target,
            VisualConditionOperatorChoices.LTE: value <= self.target,
            VisualConditionOperatorChoices.EQ: value == self.target,
            VisualConditionOperatorChoices.BETWEEN: abs(value - self.target) <= self.tolerance,
        }

        return comparisons.get(self.operator, False)

    @property
    def color(self) -> str:
        return {
            VisualConditionStateChoices.GREEN: '#198754',
            VisualConditionStateChoices.BLUE: '#0d6efd',
            VisualConditionStateChoices.YELLOW: '#ffc107',
            VisualConditionStateChoices.GREY: '#6c757d',
            VisualConditionStateChoices.RED: '#dc3545',
        }[self.state]

    @property
    def icon(self) -> str:
        return {
            VisualConditionStateChoices.GREEN: 'bi-check-circle-fill',
            VisualConditionStateChoices.BLUE: 'bi-info-circle-fill',
            VisualConditionStateChoices.YELLOW: 'bi-exclamation-triangle-fill',
            VisualConditionStateChoices.GREY: 'bi-circle-fill',
            VisualConditionStateChoices.RED: 'bi-x-circle-fill',
        }[self.state]

    def __str__(self) -> str:
        return f'{self.get_state_display()} ({self.get_operator_display()} {self.target})'

    class Meta:
        verbose_name = 'Visual Condition'
        verbose_name_plural = 'Visual Conditions'
        db_table = 'django_spire_metric_visual_condition'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=('visual', 'order'), name='unique_visual_condition_order'
            )
        ]


class VisualReference(HistoryModelMixin, ActivityMixin):
    visual = models.ForeignKey(
        Visual, on_delete=models.CASCADE, related_name='references', related_query_name='reference'
    )

    reference = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True, default='')
    order = models.PositiveSmallIntegerField(default=0)

    objects = querysets.VisualReferenceQuerySet().as_manager()
    services = VisualReferenceService()

    def __str__(self) -> str:
        return self.label or self.reference

    class Meta:
        verbose_name = 'Visual Reference'
        verbose_name_plural = 'Visual References'
        db_table = 'django_spire_metric_visual_reference'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=('visual', 'order'), name='unique_visual_reference_order'
            )
        ]
