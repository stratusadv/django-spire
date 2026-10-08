from __future__ import annotations

from decimal import Decimal

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual import forms, models
from django_spire.metric.visual.choices import VisualKindChoices
from django_spire.metric.visual.tests.factories import (
    create_test_condition,
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_subdomain,
    create_test_visual,
)


class VisualFormViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        self.visual = create_test_visual(statistic=statistic)
        self.domain = domain

    def test_create_view(self):
        response = self.client.get(reverse('django_spire:metric:visual:form:create'))
        assert response.status_code == 200

    def test_update_view(self):
        response = self.client.get(
            reverse('django_spire:metric:visual:form:update', kwargs={'pk': self.visual.pk})
        )
        assert response.status_code == 200

    def test_delete_view(self):
        response = self.client.post(
            reverse('django_spire:metric:visual:form:delete', kwargs={'pk': self.visual.pk}),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        self.visual.refresh_from_db()
        assert self.visual.is_deleted is True
        assert self.visual.activities.filter(verb='deleted').count() == 1

    def test_create_condition_view(self):
        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_condition',
                kwargs={'visual_pk': self.visual.pk},
            )
        )
        assert response.status_code == 200

    def test_create_condition_view_prefills_order_zero_without_conditions(self):
        visual = create_test_visual(statistic=self.visual.statistic, with_conditions=False)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_condition', kwargs={'visual_pk': visual.pk}
            )
        )

        assert response.context['condition'].order == 0

    def test_create_condition_view_prefills_next_order(self):
        visual = create_test_visual(statistic=self.visual.statistic, with_conditions=False)
        create_test_condition(visual, order=5)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_condition', kwargs={'visual_pk': visual.pk}
            )
        )

        assert response.context['condition'].order == 6

    def test_update_condition_view(self):
        condition = self.visual.conditions.first()

        response = self.client.get(
            reverse('django_spire:metric:visual:form:update_condition', kwargs={'pk': condition.pk})
        )
        assert response.status_code == 200

    def test_delete_condition_view(self):
        condition = self.visual.conditions.first()

        response = self.client.post(
            reverse(
                'django_spire:metric:visual:form:delete_condition', kwargs={'pk': condition.pk}
            ),
            data={'should_delete': 'on'},
        )

        assert response.status_code == 302
        condition.refresh_from_db()
        assert condition.is_deleted is True

    def test_create_reference_view_suggests_statistic_references(self):
        sub_domain = create_test_subdomain(domain=self.domain)
        self.visual.statistic.services.processor.add_value(
            reference='/home/', value=Decimal(5), sub_domain=sub_domain
        )
        self.visual.statistic.services.processor.add_value(
            reference='/dashboard/', value=Decimal(7), sub_domain=sub_domain
        )

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_reference',
                kwargs={'visual_pk': self.visual.pk},
            )
        )

        assert response.status_code == 200
        html = response.content.decode()
        assert 'id="reference-datalist"' in html
        assert '<option value="/home/">' in html
        assert '<option value="/dashboard/">' in html

    def test_create_reference_view_prefills_order_zero_without_references(self):
        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_reference',
                kwargs={'visual_pk': self.visual.pk},
            )
        )

        assert response.context['reference'].order == 0

    def test_create_reference_view_prefills_next_order(self):
        self.visual.references.create(reference='/home/', order=5)

        response = self.client.get(
            reverse(
                'django_spire:metric:visual:form:create_reference',
                kwargs={'visual_pk': self.visual.pk},
            )
        )

        assert response.context['reference'].order == 6

    def _reference_form(
        self, data: dict, instance: models.VisualReference
    ) -> forms.VisualReferenceModelForm:
        return forms.VisualReferenceModelForm(data=data, instance=instance)

    def _add_reference_value(self, reference: str = '/home/') -> None:
        sub_domain = create_test_subdomain(domain=self.domain)
        self.visual.statistic.services.processor.add_value(
            reference=reference, value=Decimal(5), sub_domain=sub_domain
        )

    def test_reference_form_rejects_duplicate_pattern(self):
        self._add_reference_value()
        self.visual.references.create(reference='/home/', order=0)

        form = self._reference_form(
            data={'visual': self.visual.pk, 'reference': '/home/', 'label': '', 'order': 1},
            instance=models.VisualReference(visual=self.visual),
        )

        assert not form.is_valid()
        assert 'reference' in form.errors

    def test_reference_form_allows_other_visuals_pattern(self):
        self._add_reference_value()
        other = create_test_visual(statistic=self.visual.statistic, name='other')
        other.references.create(reference='/home/', order=0)

        form = self._reference_form(
            data={'visual': self.visual.pk, 'reference': '/home/', 'label': '', 'order': 1},
            instance=models.VisualReference(visual=self.visual),
        )
        form.is_valid()

        assert 'reference' not in form.errors

    def test_reference_form_allows_pattern_of_deleted_reference(self):
        self._add_reference_value()
        stale = self.visual.references.create(reference='/home/', order=0)
        stale.set_deleted()

        form = self._reference_form(
            data={'visual': self.visual.pk, 'reference': '/home/', 'label': '', 'order': 1},
            instance=models.VisualReference(visual=self.visual),
        )
        form.is_valid()

        assert 'reference' not in form.errors

    def test_reference_form_allows_saving_its_own_pattern(self):
        self._add_reference_value()
        existing = self.visual.references.create(reference='/home/', label='Home', order=0)

        form = self._reference_form(
            data={'visual': self.visual.pk, 'reference': '/home/', 'label': 'Home', 'order': 0},
            instance=existing,
        )
        form.is_valid()

        assert 'reference' not in form.errors


class VisualModelFormTestCase(BaseTestCase):
    def _form(self, value: str) -> forms.VisualModelForm:
        return forms.VisualModelForm(
            data={
                'name': 'x',
                'description': 'd',
                'kind': VisualKindChoices.INDICATOR,
                'display_unit_count': value,
            }
        )

    def test_display_unit_count_accepts_bounds(self):
        for value in ('1', '104', ''):
            form = self._form(value)
            assert form.is_valid(), f'{value!r} should be valid: {form.errors}'

    def test_display_unit_count_rejects_out_of_range(self):
        for value in ('0', '105'):
            form = self._form(value)
            assert not form.is_valid(), f'{value!r} should be invalid'
            assert 'display_unit_count' in form.errors
