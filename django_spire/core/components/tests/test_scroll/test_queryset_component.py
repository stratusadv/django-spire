from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import connection
from django.template.loader import render_to_string
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django_glue import Glue
from django_glue.exceptions import GlueModelInstanceNotFoundError
from django_glue.glue.objects.django.model.object import ModelGlue
from django_glue.glue.sequence import SequenceGlue

from django_spire.api.models import ApiAccess
from django_spire.core.components.scroll import BaseScrollComponent, QuerySetScrollComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CommentScrollComponent(QuerySetScrollComponent):
    template = 'django_spire/component/scroll/scroll.html'
    item_template = 'comment/item/scroll_item.html'
    batch_size = 2

    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('name')


class GlueItemCommentScrollComponent(CommentScrollComponent):
    item_template = None
    glue_items = True

    def get_glue_item(self, item: CommentExample, name: str) -> ModelGlue:
        return Glue.model(target=item, unique_name=name, access=self.access, fields=('name',))


class UnorderedCommentScrollComponent(CommentScrollComponent):
    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.all()


class DescendingCommentScrollComponent(CommentScrollComponent):
    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('-name')


class KeptCommentScrollComponent(CommentScrollComponent):
    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.filter(name__startswith='Kept').order_by('name')


class DefaultOrderingScrollComponent(QuerySetScrollComponent):
    template = 'django_spire/component/scroll/scroll.html'
    item_template = 'comment/item/scroll_item.html'

    def get_queryset(self) -> QuerySet[ApiAccess]:
        return ApiAccess.objects.all()


class QuerySetScrollComponentTestCase(BaseTestCase):
    def _introduce(self, component: BaseScrollComponent) -> BaseScrollComponent:
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session

        return Glue.object(request, component)

    def test_items_are_model_instances(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentScrollComponent()

        items = component.get_items(0, 3)

        assert items == [comment]
        assert isinstance(items[0], CommentExample)
        assert component.get_item_key(items[0]) == comment.pk

    def test_the_glue_loads_return_glue_objects_and_the_html_loads_do_not(self) -> None:
        callables = self._introduce(CommentScrollComponent()).get_static_data()['callables']

        assert callables['load_glue_items']['returns_glue'] is True
        assert callables['load_glue_item']['returns_glue'] is True
        assert callables['load_items']['returns_glue'] is False
        assert callables['load_item']['returns_glue'] is False

    def test_a_list_uses_only_the_loads_for_its_kind_of_row(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        rendered = self._introduce(CommentScrollComponent())
        glue = self._introduce(GlueItemCommentScrollComponent())

        with pytest.raises(PermissionDenied, match='renders its rows on the server'):
            rendered.load_glue_items(offset=0)

        with pytest.raises(PermissionDenied, match='renders its rows on the server'):
            rendered.load_glue_item(key=comment.pk)

        with pytest.raises(PermissionDenied, match='sends its rows as Glue items'):
            glue.load_items(glue.request, 0)

        with pytest.raises(PermissionDenied, match='sends its rows as Glue items'):
            glue.load_item(glue.request, comment.pk)

    def test_a_glue_items_batch_holds_up_to_a_batch_of_glue_models(self) -> None:
        comments = [create_test_comment_example(name=f'Comment {number}') for number in range(5)]
        component = GlueItemCommentScrollComponent()

        batch = component.load_glue_items(offset=0)
        last_batch = component.load_glue_items(offset=4)
        past_the_end = component.load_glue_items(offset=6)

        assert isinstance(batch, SequenceGlue)
        assert [type(item) for item in batch.items] == [ModelGlue, ModelGlue]
        assert [item.instance for item in batch.items] == comments[:2]
        assert [item.name for item in batch.items] == [
            f'item_{comment.pk}' for comment in comments[:2]
        ]
        assert [item.instance for item in last_batch.items] == comments[4:]
        assert past_the_end.items == []

    def test_a_glue_items_row_is_a_glue_model_or_nothing(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = GlueItemCommentScrollComponent()

        row = component.load_glue_item(key=comment.pk)

        assert row.instance == comment
        assert row.fields == ('name',)
        assert row.name == f'item_{comment.pk}'
        assert component.load_glue_item(key=comment.pk + 1) is None

    def test_glue_items_without_get_glue_item_are_refused_by_name(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='HooklessGlueItemScrollComponent'):

            class HooklessGlueItemScrollComponent(CommentScrollComponent):
                glue_items = True

    def test_glue_items_sends_no_rows_with_the_render(self) -> None:
        create_test_comment_example(name='Budget Review')
        component = self._introduce(GlueItemCommentScrollComponent())

        with self.assertNumQueries(0):
            html = render_to_string(component.template, {'component': component})

        assert 'data-scroll-key' not in html
        assert 'rendersRows: false' in html

    def test_glue_items_take_an_item_template_drawn_in_the_browser(self) -> None:
        class TemplatedGlueItemScrollComponent(GlueItemCommentScrollComponent):
            item_template = 'task/item/task_row.html'

        component = self._introduce(TemplatedGlueItemScrollComponent())

        assert component.renders_items_on_server is False
        assert TemplatedGlueItemScrollComponent in BaseScrollComponent._validated_classes

    def test_glue_items_with_a_row_template_rendered_on_the_server_are_refused(self) -> None:
        class RenderedGlueItemScrollComponent(GlueItemCommentScrollComponent):
            item_template = 'comment/item/scroll_item.html'

        with pytest.raises(ImproperlyConfigured, match='item_template'):
            self._introduce(RenderedGlueItemScrollComponent())

    def test_an_unordered_queryset_is_listed_by_primary_key(self) -> None:
        first = create_test_comment_example(name='Zebra Notes')
        second = create_test_comment_example(name='Alpha Notes')
        third = create_test_comment_example(name='Mango Notes')
        component = UnorderedCommentScrollComponent()

        assert UnorderedCommentScrollComponent().get_queryset().ordered is False
        assert component.get_items(0, 2) == [first, second]
        assert component.get_items(2, 2) == [third]

    def test_rows_that_tie_on_the_ordering_are_each_returned_once(self) -> None:
        comments = [create_test_comment_example(name='Same Name') for _ in range(5)]
        component = CommentScrollComponent()

        with CaptureQueriesContext(connection) as queries:
            keys = [
                item.pk
                for offset in (0, 2, 4)
                for item in component.get_items(offset, 2)
            ]

        order_by = queries[0]['sql'].split('ORDER BY', 1)[1]

        assert keys == [comment.pk for comment in comments]
        assert order_by.index('"name" ASC') < order_by.index('"id" ASC')

    def test_a_descending_ordering_stays_descending(self) -> None:
        for name in ('Alpha', 'Bravo', 'Charlie'):
            create_test_comment_example(name=name)

        names = [item.name for item in DescendingCommentScrollComponent().get_items(0, 3)]

        assert names == ['Charlie', 'Bravo', 'Alpha']

    def test_a_models_default_ordering_is_kept_ahead_of_the_key(self) -> None:
        with CaptureQueriesContext(connection) as queries:
            DefaultOrderingScrollComponent().get_items(0, 3)

        order_by = queries[0]['sql'].split('ORDER BY', 1)[1]

        assert order_by.index('"name" ASC') < order_by.index('"id" ASC')

    def test_get_item_returns_a_row_only_from_inside_the_queryset(self) -> None:
        kept = create_test_comment_example(name='Kept Notes')
        dropped = create_test_comment_example(name='Dropped Notes')
        component = KeptCommentScrollComponent()

        assert component.get_item(kept.pk) == kept
        assert component.get_item(str(kept.pk)) == kept
        assert component.get_item(dropped.pk) is None
        assert component.get_item(kept.pk + dropped.pk + 1) is None
        assert component.get_item('not-a-key') is None

    def test_get_instance_returns_a_row_of_the_queryset_or_reports_it_not_found(self) -> None:
        kept = create_test_comment_example(name='Kept Notes')
        dropped = create_test_comment_example(name='Dropped Notes')
        component = KeptCommentScrollComponent()

        with self.assertNumQueries(1):
            assert component.get_instance(kept.pk) == kept

        with pytest.raises(GlueModelInstanceNotFoundError) as error:
            component.get_instance(dropped.pk)

        assert error.value.status == 404
        assert error.value.pk == dropped.pk

    def test_a_batch_costs_one_query_wherever_it_starts(self) -> None:
        for number in range(7):
            create_test_comment_example(name=f'Comment {number}')

        component = CommentScrollComponent()

        for offset in (0, 2, 6):
            with self.assertNumQueries(1):
                component.get_items(offset, 3)

    def test_a_single_row_costs_one_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        with self.assertNumQueries(1):
            assert CommentScrollComponent().get_item(comment.pk) is not None
