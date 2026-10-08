from __future__ import annotations

import pytest
from django.template import TemplateDoesNotExist

from django_spire.core.glue.components.scroll.base import ITEM_TEMPLATES, SCROLL_TEMPLATES
from django_spire.core.glue.components.scroll.templates import template_extends
from django_spire.core.tests.test_cases import BaseTestCase


class TemplateExtendsTestCase(BaseTestCase):
    def test_an_ancestor_extends_itself(self) -> None:
        assert template_extends(
            'django_spire/glue/component/scroll/base.html',
            SCROLL_TEMPLATES,
        )

    def test_a_template_that_extends_an_ancestor_directly(self) -> None:
        assert template_extends(
            'comment/component/comment_list.html',
            SCROLL_TEMPLATES,
        )
        assert template_extends(
            'django_spire/glue/component/scroll/table.html',
            SCROLL_TEMPLATES,
        )

    def test_a_template_that_reaches_an_ancestor_through_another_template(self) -> None:
        assert template_extends(
            'rest/component/pirate_table.html',
            SCROLL_TEMPLATES,
        )
        assert template_extends(
            'rest/item/pirate_row.html',
            ITEM_TEMPLATES,
        )
        assert not template_extends(
            'rest/item/pirate_row.html',
            SCROLL_TEMPLATES,
        )

    def test_a_row_template_extends_only_the_row_template_it_names(self) -> None:
        assert template_extends(
            'comment/item/scroll_item.html',
            ITEM_TEMPLATES,
        )
        assert not template_extends(
            'comment/item/scroll_item.html',
            frozenset({'django_spire/glue/component/scroll/table_row.html'}),
        )
        assert not template_extends(
            'comment/item/scroll_item.html',
            SCROLL_TEMPLATES,
        )

    def test_a_template_without_extends_does_not_extend_an_ancestor(self) -> None:
        assert not template_extends(
            'comment/item/item2.html',
            ITEM_TEMPLATES,
        )

    def test_a_template_that_extends_something_else_does_not_extend_an_ancestor(self) -> None:
        assert not template_extends(
            'comment/page/comment_list_page2.html',
            SCROLL_TEMPLATES,
        )

    def test_a_missing_template_raises(self) -> None:
        with pytest.raises(TemplateDoesNotExist):
            template_extends(
                'comment/item/does_not_exist.html',
                ITEM_TEMPLATES,
            )
