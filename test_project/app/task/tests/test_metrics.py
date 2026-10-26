from __future__ import annotations

from decimal import Decimal

import pytest
from django.test import TransactionTestCase

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup, StatisticValue

from test_project.app.task.metrics import TaskMetric
from test_project.app.task.models import Task


class TaskMetricBuildTestCase(BaseTestCase):
    def test_build_creates_declared_structure(self) -> None:
        summary = TaskMetric.build()

        assert summary.created == 10
        assert summary.errors == []

        domain = Domain.objects.for_key('tasks').get()
        assert domain.name == 'Tasks'
        assert domain.sub_domain_name == 'Sources'
        assert SubDomain.objects.for_key('tasks--manual').exists()
        assert SubDomain.objects.for_key('tasks--imported').exists()
        assert StatisticGroup.objects.for_key('tasks--lifecycle').exists()
        assert StatisticGroup.objects.for_key('tasks--throughput').exists()
        assert Statistic.objects.for_key('tasks--lifecycle--created').exists()
        assert Statistic.objects.for_key('tasks--throughput--completion-rate').get().value_type == 'percentage'
        assert Statistic.objects.for_key('tasks--throughput--estimated-hours').get().value_type == 'number'

    def test_build_is_idempotent(self) -> None:
        TaskMetric.build()
        summary = TaskMetric.build()

        assert summary.created == 0
        assert summary.updated == 0
        assert summary.unchanged == 10
        assert Domain.objects.filter(key='tasks').count() == 1
        assert Statistic.objects.filter(key__startswith='tasks--').count() == 5

    def test_check_reports_no_drift_after_build(self) -> None:
        TaskMetric.build()

        summary = TaskMetric.check()

        assert summary.ok is True
        assert summary.missing == []
        assert summary.errors == []


class TaskMetricRecordTestCase(TransactionTestCase):
    def setUp(self) -> None:
        super().setUp()
        TaskMetric.build()

    def test_record_writes_value(self) -> None:
        worker = TaskMetric.record('tasks', 'manual', 'lifecycle', 'created', reference=['task', 'created'], value=2)
        worker.join()

        value = StatisticValue.objects.get(
            statistic__key='tasks--lifecycle--created',
            sub_domain__key='tasks--manual',
        )
        assert value.reference == 'task:created'
        assert value.value == Decimal('2.0000')

    def test_record_postfixes_task_reference(self) -> None:
        task = Task.objects.create(name='Ship the release')

        worker = TaskMetric.record(
            'tasks',
            'manual',
            'lifecycle',
            'completed',
            reference=['task', 'completed'],
            source_model=task,
        )
        worker.join()

        value = StatisticValue.objects.get(
            statistic__key='tasks--lifecycle--completed',
            sub_domain__key='tasks--manual',
            reference=f'task:completed:test_project_task.task:{task.pk}',
        )
        assert value.value == Decimal('1.0000')

    def test_record_rejects_unknown_sub_domain(self) -> None:
        with pytest.raises(ValueError, match='No sub-domain'):
            TaskMetric.record('tasks', 'unknown', 'lifecycle', 'created', reference=['task', 'created'])
