from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django_glue import Glue
from django_glue.glue.objects.django.model.object import ModelGlue
from django_glue.glue.sequence import SequenceGlue

from django_spire.api.models import ApiAccess
from django_spire.core.glue.components.scroll import GlueScrollItemsMixin, QuerySetScrollComponent
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

if TYPE_CHECKING:
    from django.db.models import QuerySet


class CommentScrollComponent(QuerySetScrollComponent):
    template = 'comment/component/comment_list.html'
    batch_size = 2
    fields = ('name',)

    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('name')


class RenderedCommentScrollComponent(CommentScrollComponent):
    template = 'django_spire/glue/component/scroll/base.html'
    item_template = 'comment/item/scroll_item.html'


class GlueItemCommentScrollComponent(GlueScrollItemsMixin, CommentScrollComponent):
    pass


class FieldlessGlueItemCommentScrollComponent(GlueItemCommentScrollComponent):
    fields = ()


class WiderGlueItemCommentScrollComponent(GlueItemCommentScrollComponent):
    def get_glue_item(self, item: CommentExample, name: str, **kwargs: Any) -> ModelGlue:
        return super().get_glue_item(item, name, fields=('name', 'description'), **kwargs)


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
    template = 'django_spire/glue/component/scroll/base.html'
    item_template = 'comment/item/scroll_item.html'

    def get_queryset(self) -> QuerySet[ApiAccess]:
        return ApiAccess.objects.all()


class QuerySetScrollComponentTestCase(BaseTestCase):
    def test_data_mode_items_hold_only_the_key_and_the_listed_fields(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = CommentScrollComponent()

        items = component.get_items(0, 3)

        assert items == [{'pk': comment.pk, 'name': 'Budget Review'}]
        assert 'description' not in items[0]
        assert component.get_item_key(items[0]) == comment.pk

    def test_rendered_mode_items_are_model_instances(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = RenderedCommentScrollComponent()

        items = component.get_items(0, 3)

        assert items == [comment]
        assert isinstance(items[0], CommentExample)
        assert component.get_item_key(items[0]) == comment.pk

    def test_glue_items_declares_its_loads_as_returning_glue_objects(self) -> None:
        request = RequestFactory().get('/')
        request.user = self.super_user
        request.session = self.client.session

        glue_callables = Glue.object(
            request,
            GlueItemCommentScrollComponent(),
        ).get_static_data()['callables']
        dict_callables = Glue.object(
            request,
            CommentScrollComponent(),
        ).get_static_data()['callables']

        assert glue_callables['load_items']['returns_glue'] is True
        assert glue_callables['load_item']['returns_glue'] is True
        assert dict_callables['load_items']['returns_glue'] is False
        assert dict_callables['load_item']['returns_glue'] is False

    def test_a_glue_items_batch_holds_one_more_glue_model_than_the_batch_size(self) -> None:
        comments = [create_test_comment_example(name=f'Comment {number}') for number in range(4)]
        component = GlueItemCommentScrollComponent()

        batch = component.load_items(offset=0)
        last_batch = component.load_items(offset=2)

        assert isinstance(batch, SequenceGlue)
        assert [type(item) for item in batch.items] == [ModelGlue, ModelGlue, ModelGlue]
        assert [item.instance for item in batch.items] == comments[:3]
        assert [item.name for item in batch.items] == [
            f'item_{comment.pk}' for comment in comments[:3]
        ]
        assert [item.instance for item in last_batch.items] == comments[2:]

    def test_a_glue_items_row_is_a_glue_model_or_nothing(self) -> None:
        comment = create_test_comment_example(name='Budget Review')
        component = GlueItemCommentScrollComponent()

        assert component.load_item(key=comment.pk).instance == comment
        assert component.load_item(key=comment.pk + 1) is None

    def test_an_overridden_glue_item_passes_its_options_through_super(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        default_item = GlueItemCommentScrollComponent().load_item(key=comment.pk)
        wider_item = WiderGlueItemCommentScrollComponent().load_item(key=comment.pk)

        assert default_item.fields == ('name',)
        assert wider_item.fields == ('name', 'description')
        assert wider_item.instance == comment
        assert wider_item.name == f'item_{comment.pk}'

    def test_glue_items_without_fields_are_refused_by_name(self) -> None:
        create_test_comment_example(name='Budget Review')

        with pytest.raises(ImproperlyConfigured, match='FieldlessGlueItemCommentScrollComponent'):
            FieldlessGlueItemCommentScrollComponent().load_items(offset=0)

    def test_glue_items_sends_no_first_batch_with_the_render(self) -> None:
        create_test_comment_example(name='Budget Review')

        with self.assertNumQueries(0):
            assert GlueItemCommentScrollComponent().first_batch_data is None

        assert CommentScrollComponent().first_batch_data['keys'] != []

    def test_glue_items_with_an_item_template_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='with an item_template'):

            class RenderedGlueItemScrollComponent(
                GlueScrollItemsMixin,
                RenderedCommentScrollComponent,
            ):
                pass

    def test_an_unordered_queryset_is_refused(self) -> None:
        create_test_comment_example(name='Budget Review')

        with pytest.raises(ImproperlyConfigured, match='ordered'):
            UnorderedCommentScrollComponent().get_items(0, 3)

        assert len(CommentScrollComponent().get_items(0, 3)) == 1

    def test_rows_that_tie_on_the_ordering_are_each_returned_once(self) -> None:
        comments = [create_test_comment_example(name='Same Name') for _ in range(5)]
        component = RenderedCommentScrollComponent()

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

        names = [item['name'] for item in DescendingCommentScrollComponent().get_items(0, 3)]

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

        assert component.get_item(kept.pk) == {'pk': kept.pk, 'name': 'Kept Notes'}
        assert component.get_item(str(kept.pk)) == {'pk': kept.pk, 'name': 'Kept Notes'}
        assert component.get_item(dropped.pk) is None
        assert component.get_item(kept.pk + dropped.pk + 1) is None
        assert component.get_item('not-a-key') is None

    def test_a_batch_costs_one_query_wherever_it_starts(self) -> None:
        for number in range(7):
            create_test_comment_example(name=f'Comment {number}')

        for component_class in (CommentScrollComponent, RenderedCommentScrollComponent):
            component = component_class()

            for offset in (0, 2, 6):
                with self.assertNumQueries(1):
                    component.get_items(offset, 3)

    def test_a_single_row_costs_one_query(self) -> None:
        comment = create_test_comment_example(name='Budget Review')

        for component_class in (CommentScrollComponent, RenderedCommentScrollComponent):
            with self.assertNumQueries(1):
                assert component_class().get_item(comment.pk) is not None
