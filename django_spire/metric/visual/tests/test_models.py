from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import (
    AreaChartVisual,
    BarChartVisual,
    GaugeChartVisual,
    IndicatorVisual,
    LineChartVisual,
    PieChartVisual,
    Visual,
    VisualCondition,
    VisualReference,
)
from django_spire.metric.visual.tests.factories import (
    create_test_statistic,
    create_test_statistic_group,
    create_test_domain,
    create_test_visual,
)


class VisualModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)

    def test_str(self):
        assert str(self.visual) == self.visual.name

    def test_statistic_relation(self):
        assert self.visual.statistic is not None

    def test_statistic_nullable(self):
        visual = Visual.objects.create(name='empty')
        assert visual.statistic is None

    def test_conditions_relation(self):
        assert self.visual.conditions.count() == 3

    def test_kind_defaults_to_indicator(self):
        assert self.visual.kind == 'indicator'
        assert self.visual.is_chart is False

    def test_kind_mapping_and_upcast(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, kind='line')

        assert Visual.kind_model('line') is LineChartVisual
        assert Visual.subclass_for(visual).__class__ is LineChartVisual

    def test_proxy_manager_filters_by_kind_and_pins_on_save(self):
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)

        line_visual = LineChartVisual.objects.create(name='line', statistic=statistic)

        assert line_visual.kind == 'line'
        assert line_visual not in IndicatorVisual.objects.all()
        assert list(LineChartVisual.objects.all()) == [line_visual]
        assert LineChartVisual.objects.count() == 1
        assert GaugeChartVisual.objects.count() == 0

        other = create_test_visual(statistic=statistic)
        assert line_visual.pk != other.pk
        assert other.kind == 'indicator'
        assert GaugeChartVisual.objects.count() == 0


class VisualKindModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        self.statistic = create_test_statistic(group=group)

    def test_kind_model_registry_covers_all_proxies(self):
        assert Visual.kind_model('indicator') is IndicatorVisual
        assert Visual.kind_model('line') is LineChartVisual
        assert Visual.kind_model('bar') is BarChartVisual
        assert Visual.kind_model('area') is AreaChartVisual
        assert Visual.kind_model('pie') is PieChartVisual
        assert Visual.kind_model('gauge') is GaugeChartVisual

    def test_subclass_for_unknown_kind_returns_base(self):
        assert Visual.kind_model('unknown') is Visual


class VisualConditionModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic, with_conditions=False)

    def test_str(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gt', target=Decimal(100), order=0
        )
        assert str(condition) == 'Green (Greater Than 100)'

    def test_services_is_condition_service(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gt', target=Decimal(100), order=0
        )
        assert condition.services.transformation.matches(Decimal(101)) is True

    def test_matches_gt(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gt', target=Decimal(100), order=0
        )
        assert condition.matches(Decimal(101))
        assert not condition.matches(Decimal(100))

    def test_matches_gte(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gte', target=Decimal(100), order=0
        )
        assert condition.matches(Decimal(100))

    def test_matches_lt(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='red', operator='lt', target=Decimal(100), order=0
        )
        assert condition.matches(Decimal(99))
        assert not condition.matches(Decimal(100))

    def test_matches_lte(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='red', operator='lte', target=Decimal(100), order=0
        )
        assert condition.matches(Decimal(100))

    def test_matches_eq(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='red', operator='eq', target=Decimal(100), order=0
        )
        assert condition.matches(Decimal(100))
        assert not condition.matches(Decimal(101))

    def test_matches_between_within_tolerance(self):
        condition = VisualCondition.objects.create(
            visual=self.visual,
            state='yellow',
            operator='between',
            target=Decimal(100),
            tolerance=Decimal(10),
            order=0,
        )
        assert condition.matches(Decimal(105))
        assert condition.matches(Decimal(90))
        assert not condition.matches(Decimal(89))

    def test_color_mapping(self):
        green = VisualCondition.objects.create(
            visual=self.visual, state='green', operator='gt', target=Decimal(100), order=0
        )
        blue = VisualCondition.objects.create(
            visual=self.visual, state='blue', operator='gt', target=Decimal(100), order=1
        )
        red = VisualCondition.objects.create(
            visual=self.visual, state='red', operator='lt', target=Decimal(100), order=2
        )
        grey = VisualCondition.objects.create(
            visual=self.visual, state='grey', operator='lt', target=Decimal(100), order=3
        )
        assert green.color == '#198754'
        assert blue.color == '#0d6efd'
        assert red.color == '#dc3545'
        assert grey.color == '#6c757d'

    def test_icon_mapping(self):
        condition = VisualCondition.objects.create(
            visual=self.visual, state='yellow', operator='between', target=Decimal(100), order=0
        )
        assert condition.icon == 'bi-exclamation-triangle-fill'

    def test_icon_mapping_blue_and_grey(self):
        blue = VisualCondition.objects.create(
            visual=self.visual, state='blue', operator='gt', target=Decimal(100), order=0
        )
        grey = VisualCondition.objects.create(
            visual=self.visual, state='grey', operator='lt', target=Decimal(100), order=1
        )
        assert blue.icon == 'bi-info-circle-fill'
        assert grey.icon == 'bi-circle-fill'


class VisualReferenceModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic, references=['/home/', '/dashboard/'])

    def test_references_relation_ordered(self):
        assert [ref.reference for ref in self.visual.references.all()] == ['/home/', '/dashboard/']

    def test_str_uses_label_when_present(self):
        reference = VisualReference.objects.create(
            visual=self.visual, reference='helpdesk:page:%', label='Helpdesk Pages', order=5
        )
        assert str(reference) == 'Helpdesk Pages'

    def test_str_falls_back_to_reference(self):
        reference = VisualReference.objects.create(
            visual=self.visual, reference='/contact/', order=5
        )
        assert str(reference) == '/contact/'

    def test_order_unique_per_visual(self):
        VisualReference.objects.create(visual=self.visual, reference='/a/', order=9)

        with pytest.raises(IntegrityError):
            VisualReference.objects.create(visual=self.visual, reference='/b/', order=9)
