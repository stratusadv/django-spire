from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.comment.navigation import CommentNavigation
from django_spire.core.components import ModelCrudScrollComponent, PageItemFormOptions
from test_project.app.comment.models import CommentExample

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class CommentListComponent(ModelCrudScrollComponent):
    template = 'comment/component/comment_list.html'
    view_template = 'comment/page/comment_list_page2.html'
    fields = ('name', 'description')
    item_form_options = PageItemFormOptions('comment:page:form')

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        nav = CommentNavigation()
        nav.page_title = 'Comment'
        self.context_data.update(nav.as_context())

    def get_queryset(self) -> QuerySet[CommentExample]:
        return CommentExample.objects.order_by('id')
