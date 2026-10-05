from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from django_glue import Glue

from django_spire.comment.navigation import CommentNavigation
from django_spire.core.glue.components.scroll_component import BaseScrollComponent
from test_project.app.comment.models import CommentExample

if TYPE_CHECKING:
    from django.http import HttpRequest


class CommentListComponent(BaseScrollComponent):
    template = 'comment/component/comment_list.html'
    layout_template = 'comment/page/comment_list_page2.html'

    amount_loaded: int = Glue.attr(0)

    # comment_list = Glue.queryset(
    #         request=None,
    #         target=CommentExample.objects.all(),
    #         unique_name='comment_examples',
    #         access=Glue.Access.CHANGE,
    #         fields=['id', 'name', 'description'],
    #         batch_size=50,
    #     )

    @classmethod
    def get_view_kwargs(cls, request: HttpRequest, **url_kwargs: Any) -> dict[str, Any]:
        return {**super().get_view_kwargs(request, **url_kwargs), 'access': Glue.Access.VIEW}

    def get_context_data(self) -> dict[str, Any]:
        nav = CommentNavigation()
        nav.page_title = 'Comment'
        return {**super().get_context_data(), **nav.as_context()}

    @cached_property
    def comment_examples(self) -> list[CommentExample]:
        return list(CommentExample.objects.all())

    @Glue.attr
    def get_items(self, reset: bool = False) -> list[dict[str, Any]]:
        batch_size = 25

        if reset:
            print('reset')
            self.amount_loaded = 0

        comment_list = list(
            CommentExample.objects.all().values('id', 'name', 'description')[:self.amount_loaded + batch_size])
        print(self.amount_loaded)

        self.amount_loaded += batch_size

        return comment_list

    @Glue.attr
    def on_item_updated(self, *updated_item_event_kwargs):
        return None

    @Glue.property
    def has_more(self):
        print(f'count: {CommentExample.objects.count()}')
        return CommentExample.objects.count() > self.amount_loaded
