from __future__ import annotations

from django.db import IntegrityError

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.signage.models import Signage, SignagePresentation
from django_spire.metric.visual.signage.tests.factories import create_test_link, create_test_signage


class SignageModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()

    def test_str(self):
        assert str(self.signage) == self.signage.name

    def test_key_auto_generated(self):
        assert self.signage.key is not None

    def test_key_unique(self):
        with pytest.raises(IntegrityError):
            Signage.objects.create(name='dup', key=self.signage.key)

    def test_set_deleted_deletes_links(self):
        link = create_test_link(self.signage)

        self.signage.set_deleted()

        self.signage.refresh_from_db()
        link.refresh_from_db()

        assert self.signage.is_deleted is True
        assert link.is_deleted is True


class SignagePresentationModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.signage = create_test_signage()
        self.link = create_test_link(self.signage)

    def test_str(self):
        assert str(self.link) == f'{self.signage} - {self.link.presentation}'

    def test_signage_relation(self):
        assert self.link.signage == self.signage
        assert self.signage.presentations.filter(pk=self.link.presentation.pk).exists()

    def test_unique_order_per_signage(self):
        with pytest.raises(IntegrityError):
            create_test_link(self.signage, order=self.link.order)

    def test_ordering(self):
        create_test_link(self.signage, order=2)
        create_test_link(self.signage, order=1)

        links = SignagePresentation.objects.for_signage(self.signage)

        assert [link.order for link in links] == [0, 1, 2]
