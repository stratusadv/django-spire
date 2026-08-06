from __future__ import annotations

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
