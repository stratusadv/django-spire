from __future__ import annotations

import uuid

from django.test import RequestFactory
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.domain.statistic import forms
from django_spire.metric.domain.statistic.models import Statistic, StatisticGroup
from django_spire.metric.domain.statistic.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
)


class StatisticGroupFormViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)

    def test_group_create_view(self):
        response = self.client.get(
            path=reverse('django_spire:metric:domain:statistic:form:group_create')
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/group_form_page.html'
        )

    def test_group_create_save_model_obj(self):
        form = forms.StatisticGroupForm(
            data={
                'domain': self.domain.pk,
                'name': 'new group',
                'description': 'new group description',
            }
        )
        assert form.is_valid()

        response = form.save_model_obj(RequestFactory().get('/'))

        group = StatisticGroup.objects.get(name='new group')
        assert group.domain == self.domain
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': group.pk}
        )

    def test_group_update_view(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:group_update',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/group_form_page.html'
        )

    def test_group_update_save_model_obj(self):
        form = forms.StatisticGroupForm(
            instance=self.group,
            data={
                'domain': self.domain.pk,
                'name': 'updated group',
                'description': 'updated description',
            },
        )
        assert form.is_valid()

        response = form.save_model_obj(RequestFactory().get('/'))

        self.group.refresh_from_db()
        assert self.group.name == 'updated group'
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': self.group.pk}
        )

    def test_group_delete_view(self):
        response = self.client.post(
            reverse(
                'django_spire:metric:domain:statistic:form:group_delete',
                kwargs={'pk': self.group.pk},
            )
        )
        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:statistic:page:group_list')

        self.group.refresh_from_db()
        assert self.group.is_deleted


class StatisticFormViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()
        self.group = create_test_statistic_group(domain=self.domain)
        self.statistic = create_test_statistic(group=self.group)

    def test_create_view(self):
        response = self.client.get(path=reverse('django_spire:metric:domain:statistic:form:create'))
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/statistic_form_page.html'
        )

    def test_create_save_model_obj(self):
        form = forms.StatisticForm(
            data={'group': self.group.pk, 'name': 'new statistic', 'interval': 'daily'}
        )
        assert form.is_valid()

        response = form.save_model_obj(RequestFactory().get('/'))

        statistic = Statistic.objects.get(name='new statistic')
        assert statistic.group == self.group
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': self.group.pk}
        )

    def test_update_view(self):
        response = self.client.get(
            path=reverse(
                'django_spire:metric:domain:statistic:form:update', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 200
        self.assertTemplateUsed(
            response, 'django_spire/metric/domain/statistic/page/statistic_form_page.html'
        )

    def test_update_save_model_obj(self):
        form = forms.StatisticForm(
            instance=self.statistic,
            data={'group': self.group.pk, 'name': 'updated statistic', 'interval': 'weekly'},
        )
        assert form.is_valid()

        response = form.save_model_obj(RequestFactory().get('/'))

        self.statistic.refresh_from_db()
        assert self.statistic.name == 'updated statistic'
        assert self.statistic.interval == 'weekly'
        assert response.result['redirect_url'] == reverse(
            'django_spire:metric:domain:statistic:page:group_detail', kwargs={'pk': self.group.pk}
        )

    def test_create_save_model_obj_with_custom_key(self):
        form = forms.StatisticForm(
            data={
                'key': '22222222-3333-4444-8555-666666666601',
                'group': self.group.pk,
                'name': 'new statistic',
                'interval': 'daily',
            }
        )
        assert form.is_valid()

        form.save_model_obj(RequestFactory().get('/'))

        statistic = Statistic.objects.get(name='new statistic')
        assert statistic.key == uuid.UUID('22222222-3333-4444-8555-666666666601')

    def test_create_save_model_obj_blank_key_uses_uuid4(self):
        form = forms.StatisticForm(
            data={'key': '', 'group': self.group.pk, 'name': 'new statistic', 'interval': 'daily'}
        )
        assert form.is_valid()

        form.save_model_obj(RequestFactory().get('/'))

        statistic = Statistic.objects.get(name='new statistic')
        assert statistic.key is not None
        assert statistic.key.version == 4

    def test_create_save_model_obj_duplicate_key_is_invalid(self):
        existing = Statistic.objects.create(
            group=self.group,
            name='existing statistic',
            key=uuid.UUID('22222222-3333-4444-8555-666666666601'),
        )

        form = forms.StatisticForm(
            data={
                'key': '22222222-3333-4444-8555-666666666601',
                'group': self.group.pk,
                'name': 'new statistic',
                'interval': 'daily',
            }
        )
        assert not form.is_valid()
        assert 'key' in form.errors
        assert Statistic.objects.filter(key=existing.key).count() == 1

    def test_create_save_model_obj_non_uuid4_key_is_invalid(self):
        form = forms.StatisticForm(
            data={
                'key': '123e4567-e89b-12d3-a456-426614174000',
                'group': self.group.pk,
                'name': 'new statistic',
                'interval': 'daily',
            }
        )
        assert not form.is_valid()
        assert 'key' in form.errors

    def test_update_save_model_obj_blank_key_preserves_existing_key(self):
        original_key = self.statistic.key

        form = forms.StatisticForm(
            instance=self.statistic,
            data={
                'key': '',
                'group': self.group.pk,
                'name': 'updated statistic',
                'interval': 'weekly',
            },
        )
        assert form.is_valid()

        form.save_model_obj(RequestFactory().get('/'))

        self.statistic.refresh_from_db()
        assert self.statistic.key == original_key

    def test_update_save_model_obj_custom_key_changes_key(self):
        form = forms.StatisticForm(
            instance=self.statistic,
            data={
                'key': '22222222-3333-4444-8555-666666666602',
                'group': self.group.pk,
                'name': 'updated statistic',
                'interval': 'weekly',
            },
        )
        assert form.is_valid()

        form.save_model_obj(RequestFactory().get('/'))

        self.statistic.refresh_from_db()
        assert self.statistic.key == uuid.UUID('22222222-3333-4444-8555-666666666602')

    def test_create_save_model_obj_with_value_type(self):
        form = forms.StatisticForm(
            data={
                'group': self.group.pk,
                'name': 'new statistic',
                'interval': 'daily',
                'value_type': 'currency',
            }
        )
        assert form.is_valid()

        form.save_model_obj(RequestFactory().get('/'))

        statistic = Statistic.objects.get(name='new statistic')
        assert statistic.value_type == 'currency'

    def test_delete_view(self):
        response = self.client.post(
            reverse(
                'django_spire:metric:domain:statistic:form:delete', kwargs={'pk': self.statistic.pk}
            )
        )
        assert response.status_code == 302
        assert response.url == reverse('django_spire:metric:domain:statistic:page:list')

        self.statistic.refresh_from_db()
        assert self.statistic.is_deleted
