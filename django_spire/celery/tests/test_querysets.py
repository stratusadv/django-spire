from __future__ import annotations

from celery import states

from django.test import TestCase

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_celery_task


class CeleryTaskQuerySetByReferenceKeyTestCase(TestCase):
    def setUp(self) -> None:
        self.reference_key_1 = 'key1'
        self.reference_key_2 = 'key2'

        self.task1 = create_celery_task(reference_key=self.reference_key_1)
        self.task2 = create_celery_task(reference_key=self.reference_key_2)
        self.task3 = create_celery_task(reference_key=self.reference_key_1)

    def test_by_reference_keys_returns_matching_tasks(self) -> None:
        result = CeleryTask.objects.by_reference_keys([self.reference_key_1])

        assert self.task1 in result
        assert self.task3 in result
        assert self.task2 not in result

    def test_by_reference_keys_returns_correct_count(self) -> None:
        result = CeleryTask.objects.by_reference_keys([self.reference_key_1])

        assert result.count() == 2

    def test_by_reference_keys_returns_empty_when_no_match(self) -> None:
        result = CeleryTask.objects.by_reference_keys(['nonexistent_key'])

        assert result.count() == 0

    def test_by_reference_keys_chaining(self) -> None:
        result = CeleryTask.objects.by_reference_keys(
            [self.reference_key_1]
        ).by_reference_keys([self.reference_key_1])

        assert result.count() == 2


class CeleryTaskQuerySetByModelKeyTestCase(TestCase):
    def setUp(self) -> None:
        self.model_key_1 = 'model_key_1'
        self.model_key_2 = 'model_key_2'

        self.task1 = create_celery_task(model_key=self.model_key_1)
        self.task2 = create_celery_task(model_key=self.model_key_2)
        self.task3 = create_celery_task(model_key=self.model_key_1)

    def test_by_model_keys_returns_matching_tasks(self) -> None:
        result = CeleryTask.objects.by_model_keys([self.model_key_1])

        assert self.task1 in result
        assert self.task3 in result
        assert self.task2 not in result

    def test_by_model_keys_returns_correct_count(self) -> None:
        result = CeleryTask.objects.by_model_keys([self.model_key_1])

        assert result.count() == 2

    def test_by_model_keys_returns_empty_when_no_match(self) -> None:
        result = CeleryTask.objects.by_model_keys(['nonexistent_model_key'])

        assert result.count() == 0


class CeleryTaskQuerySetByReferenceAndModelKeyTestCase(TestCase):
    def setUp(self) -> None:
        self.reference_key_1 = 'ref_key_1'
        self.reference_key_2 = 'ref_key_2'
        self.model_key_1 = 'model_key_1'
        self.model_key_2 = 'model_key_2'

        self.task1 = create_celery_task(
            reference_key=self.reference_key_1, model_key=self.model_key_1
        )
        self.task2 = create_celery_task(
            reference_key=self.reference_key_2, model_key=self.model_key_2
        )
        self.task3 = create_celery_task(
            reference_key=self.reference_key_1, model_key=self.model_key_2
        )
        self.task4 = create_celery_task(reference_key=self.reference_key_1, model_key=None)

    def test_by_reference_keys_model_keys_with_model_key(self) -> None:
        ref_model_map = {self.reference_key_1: self.model_key_1}
        result = CeleryTask.objects.by_reference_keys_model_keys(ref_model_map)

        assert self.task1 in result
        assert self.task3 not in result
        assert self.task4 not in result

    def test_by_reference_keys_model_keys_without_model_key(self) -> None:
        ref_model_map = {self.reference_key_1: None}
        result = CeleryTask.objects.by_reference_keys_model_keys(ref_model_map)

        assert self.task4 in result
        assert self.task1 not in result

    def test_by_reference_keys_model_keys_multiple_keys(self) -> None:
        ref_model_map = {
            self.reference_key_1: self.model_key_1,
            self.reference_key_2: self.model_key_2,
        }
        result = CeleryTask.objects.by_reference_keys_model_keys(ref_model_map)

        assert self.task1 in result
        assert self.task2 in result
        assert self.task3 not in result


class CeleryTaskQuerySetByUnreadyTestCase(TestCase):
    def setUp(self) -> None:
        self.task_pending = create_celery_task(state=states.PENDING)
        self.task_started = create_celery_task(state=states.STARTED)
        self.task_success = create_celery_task(state=states.SUCCESS)
        self.task_failure = create_celery_task(state=states.FAILURE)
        self.task_revoked = create_celery_task(state=states.REVOKED)

    def test_by_unready_returns_pending(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert self.task_pending in result

    def test_by_unready_returns_started(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert self.task_started in result

    def test_by_unready_excludes_success(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert self.task_success not in result

    def test_by_unready_excludes_failure(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert self.task_failure not in result

    def test_by_unready_excludes_revoked(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert self.task_revoked not in result

    def test_by_unready_count(self) -> None:
        result = CeleryTask.objects.by_unready()

        assert result.count() == 2

    def test_by_unready_chaining_with_by_reference_keys(self) -> None:
        reference_key = 'test_key'
        task1 = create_celery_task(reference_key=reference_key, state=states.PENDING)
        task2 = create_celery_task(reference_key=reference_key, state=states.SUCCESS)

        result = CeleryTask.objects.by_reference_keys([reference_key]).by_unready()

        assert task1 in result
        assert task2 not in result
        assert result.count() == 1