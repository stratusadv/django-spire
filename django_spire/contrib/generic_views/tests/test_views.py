from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase

from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.contrib.generic_views.modal_views import dispatch_modal_delete_form_content
from django_spire.contrib.generic_views.portal_views import (
    delete_form_view,
    detail_view,
    form_view,
    infinite_scrolling_view,
    list_view,
    model_form_view,
    template_view,
)


class TestDispatchModalDeleteFormContent(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.obj = MagicMock()
        self.obj._meta.model._meta.verbose_name = 'Test Model'
        self.obj.__str__ = MagicMock(return_value='Test Object')

    def test_get_request_returns_template_response(self) -> None:
        request = self.factory.get('/')
        request.user = self.user

        response = dispatch_modal_delete_form_content(
            request,
            obj=self.obj,
            form_action='/delete/'
        )

        assert isinstance(response, TemplateResponse)

    def test_get_request_context_contains_form_data(self) -> None:
        request = self.factory.get('/')
        request.user = self.user

        response = dispatch_modal_delete_form_content(
            request,
            obj=self.obj,
            form_action='/delete/'
        )

        assert 'form_title' in response.context_data
        assert 'form_action' in response.context_data
        assert 'form_description' in response.context_data

    def test_post_request_returns_redirect(self) -> None:
        request = self.factory.post('/', data={'should_delete': True})
        request.user = self.user

        del self.obj.add_activity

        with patch('django_spire.contrib.generic_views.modal_views.safe_redirect_url', return_value='/'):
            response = dispatch_modal_delete_form_content(
                request,
                obj=self.obj,
                form_action='/delete/'
            )

        assert isinstance(response, HttpResponseRedirect)

    def test_custom_verbs(self) -> None:
        request = self.factory.get('/')
        request.user = self.user

        response = dispatch_modal_delete_form_content(
            request,
            obj=self.obj,
            form_action='/archive/',
            verbs=('archive', 'archived')
        )

        assert 'Archive' in response.context_data['form_title']

    def test_custom_return_url(self) -> None:
        request = self.factory.post('/', data={'should_delete': True})
        request.user = self.user

        del self.obj.add_activity

        response = dispatch_modal_delete_form_content(
            request,
            obj=self.obj,
            form_action='/delete/',
            return_url='/custom/'
        )

        assert response.url == '/custom/'


class TestDetailView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.obj = MagicMock()
        self.obj._meta.model._meta.verbose_name = 'Test Model'
        self.obj.__str__ = MagicMock(return_value='Test Object')
        del self.obj.breadcrumbs

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')

        response = detail_view(
            request,
            obj=self.obj,
            template='test_template.html'
        )

        assert isinstance(response, TemplateResponse)

    def test_context_contains_page_data(self) -> None:
        request = self.factory.get('/')

        response = detail_view(
            request,
            obj=self.obj,
            template='test_template.html'
        )

        assert 'page_title' in response.context_data
        assert 'page_description' in response.context_data
        assert 'breadcrumbs' in response.context_data

    def test_custom_breadcrumbs_func(self) -> None:
        request = self.factory.get('/')

        def breadcrumbs_func(breadcrumbs: Breadcrumbs) -> None:
            breadcrumbs.add_breadcrumb('Custom', '/custom/')

        response = detail_view(
            request,
            obj=self.obj,
            template='test_template.html',
            breadcrumbs_func=breadcrumbs_func
        )

        assert len(response.context_data['breadcrumbs']) == 1


class TestDeleteFormView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.obj = MagicMock()
        self.obj._meta.model._meta.verbose_name = 'Test Model'
        self.obj.__str__ = MagicMock(return_value='Test Object')
        del self.obj.breadcrumbs

    def test_get_request_returns_template_response(self) -> None:
        request = self.factory.get('/')
        request.user = self.user

        response = delete_form_view(
            request,
            obj=self.obj,
            return_url='/'
        )

        assert isinstance(response, TemplateResponse)

    def test_post_with_should_delete_redirects(self) -> None:
        request = self.factory.post('/', data={'should_delete': True})
        request.user = self.user

        del self.obj.add_activity

        response = delete_form_view(
            request,
            obj=self.obj,
            return_url='/list/'
        )

        assert isinstance(response, HttpResponseRedirect)
        assert response.url == '/list/'

    def test_post_calls_set_deleted(self) -> None:
        request = self.factory.post('/', data={'should_delete': True})
        request.user = self.user

        del self.obj.add_activity

        delete_form_view(
            request,
            obj=self.obj,
            return_url='/'
        )

        self.obj.set_deleted.assert_called_once()


class TestInfiniteScrollingView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')

        response = infinite_scrolling_view(
            request,
            queryset=[1, 2, 3, 4, 5],
            queryset_name='items',
            template='test_template.html'
        )

        assert isinstance(response, TemplateResponse)

    def test_pagination_first_page(self) -> None:
        request = self.factory.get('/', {'page': '1'})

        response = infinite_scrolling_view(
            request,
            queryset=list(range(100)),
            queryset_name='items',
            template='test_template.html'
        )

        assert len(response.context_data['items']) == 50
        assert response.context_data['has_next'] is True

    def test_pagination_last_page(self) -> None:
        request = self.factory.get('/', {'page': '2'})

        response = infinite_scrolling_view(
            request,
            queryset=list(range(60)),
            queryset_name='items',
            template='test_template.html'
        )

        assert len(response.context_data['items']) == 10
        assert response.context_data['has_next'] is False

    def test_custom_batch_size(self) -> None:
        request = self.factory.get('/', {'batch_size': '10'})

        response = infinite_scrolling_view(
            request,
            queryset=list(range(25)),
            queryset_name='items',
            template='test_template.html'
        )

        assert len(response.context_data['items']) == 10
        assert response.context_data['batch_size'] == 10

    def test_total_count_in_context(self) -> None:
        request = self.factory.get('/')

        response = infinite_scrolling_view(
            request,
            queryset=list(range(75)),
            queryset_name='items',
            template='test_template.html'
        )

        assert response.context_data['total_count'] == 75


class TestListView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.model = MagicMock()
        self.model._meta.verbose_name = 'Test Model'

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')

        response = list_view(
            request,
            model=self.model,
            template='test_template.html'
        )

        assert isinstance(response, TemplateResponse)

    def test_context_contains_page_data(self) -> None:
        request = self.factory.get('/')

        response = list_view(
            request,
            model=self.model,
            template='test_template.html'
        )

        assert response.context_data['page_title'] == 'Test Model'
        assert response.context_data['page_description'] == 'List View'
        assert 'breadcrumbs' in response.context_data

    def test_custom_breadcrumbs_func(self) -> None:
        request = self.factory.get('/')

        def breadcrumbs_func(breadcrumbs: Breadcrumbs) -> None:
            breadcrumbs.add_breadcrumb('Custom List', '/list/')

        response = list_view(
            request,
            model=self.model,
            template='test_template.html',
            breadcrumbs_func=breadcrumbs_func
        )

        assert len(response.context_data['breadcrumbs']) == 1


class TestFormView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.obj = MagicMock()
        self.obj._meta.model._meta.verbose_name = 'Test Model'
        self.obj.__str__ = MagicMock(return_value='Test Object')
        self.obj.pk = 1
        del self.obj.breadcrumbs
        self.form = MagicMock()

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')

        response = form_view(
            request,
            form=self.form,
            obj=self.obj
        )

        assert isinstance(response, TemplateResponse)

    def test_edit_verb_for_existing_object(self) -> None:
        request = self.factory.get('/')

        response = form_view(
            request,
            form=self.form,
            obj=self.obj
        )

        assert 'Edit' in response.context_data['form_title']

    def test_create_verb_for_new_object(self) -> None:
        request = self.factory.get('/')
        self.obj.pk = None

        response = form_view(
            request,
            form=self.form,
            obj=self.obj
        )

        assert 'Create' in response.context_data['form_title']

    def test_custom_verb(self) -> None:
        request = self.factory.get('/')

        response = form_view(
            request,
            form=self.form,
            obj=self.obj,
            verb='Update'
        )

        assert 'Update' in response.context_data['form_title']


class TestModelFormView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.obj = MagicMock()
        self.obj._meta.model._meta.verbose_name = 'Test Model'
        self.obj.__str__ = MagicMock(return_value='Test Object')
        self.obj.pk = 1
        del self.obj.breadcrumbs
        self.form = MagicMock()

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')

        response = model_form_view(
            request,
            form=self.form,
            obj=self.obj
        )

        assert isinstance(response, TemplateResponse)

    def test_delegates_to_form_view(self) -> None:
        request = self.factory.get('/')

        response = model_form_view(
            request,
            form=self.form,
            obj=self.obj
        )

        assert 'form' in response.context_data
        assert 'breadcrumbs' in response.context_data


class TestTemplateView(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_returns_template_response(self) -> None:
        request = self.factory.get('/')
        breadcrumbs = Breadcrumbs()

        response = template_view(
            request,
            page_title='Test Page',
            page_description='Test Description',
            breadcrumbs=breadcrumbs,
            template='test_template.html'
        )

        assert isinstance(response, TemplateResponse)

    def test_context_contains_page_data(self) -> None:
        request = self.factory.get('/')
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/')

        response = template_view(
            request,
            page_title='Test Page',
            page_description='Test Description',
            breadcrumbs=breadcrumbs,
            template='test_template.html'
        )

        assert response.context_data['page_title'] == 'Test Page'
        assert response.context_data['page_description'] == 'Test Description'
        assert len(response.context_data['breadcrumbs']) == 1

    def test_custom_context_data(self) -> None:
        request = self.factory.get('/')
        breadcrumbs = Breadcrumbs()

        response = template_view(
            request,
            page_title='Test Page',
            page_description='Test Description',
            breadcrumbs=breadcrumbs,
            template='test_template.html',
            context_data={'custom_key': 'custom_value'}
        )

        assert response.context_data['custom_key'] == 'custom_value'
