from __future__ import annotations

from unittest.mock import MagicMock

from django.test import TestCase

from django_spire.contrib.breadcrumb.breadcrumbs import BreadcrumbItem, Breadcrumbs


class TestBreadcrumbItem(TestCase):
    def test_create_with_href(self) -> None:
        item = BreadcrumbItem(name='Home', href='/home/')

        assert item.name == 'Home'
        assert item.href == '/home/'

    def test_create_without_href(self) -> None:
        item = BreadcrumbItem(name='Current Page')

        assert item.name == 'Current Page'
        assert item.href is None

    def test_to_dict(self) -> None:
        item = BreadcrumbItem(name='Home', href='/home/')
        result = item.to_dict()

        assert result == {'name': 'Home', 'href': '/home/'}

    def test_to_dict_without_href(self) -> None:
        item = BreadcrumbItem(name='Current Page')
        result = item.to_dict()

        assert result == {'name': 'Current Page', 'href': None}


class TestBreadcrumbs(TestCase):
    def test_add_base_breadcrumb(self) -> None:
        breadcrumbs = Breadcrumbs()

        model = MagicMock()
        model_breadcrumbs = Breadcrumbs()
        model_breadcrumbs.add_breadcrumb('Base', '/base/')
        model.base_breadcrumb.return_value = model_breadcrumbs

        breadcrumbs.add_base_breadcrumb(model)

        assert len(breadcrumbs) == 1

    def test_add_base_breadcrumb_no_method(self) -> None:
        breadcrumbs = Breadcrumbs()

        model = MagicMock(spec=[])

        breadcrumbs.add_base_breadcrumb(model)

        assert len(breadcrumbs) == 0

    def test_add_breadcrumb(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/home/')

        assert len(breadcrumbs) == 1
        assert breadcrumbs.data[0].name == 'Home'
        assert breadcrumbs.data[0].href == '/home/'

    def test_add_breadcrumb_without_href(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Current Page')

        assert len(breadcrumbs) == 1
        assert breadcrumbs.data[0].name == 'Current Page'
        assert breadcrumbs.data[0].href is None

    def test_add_form_breadcrumbs_create(self) -> None:
        breadcrumbs = Breadcrumbs()

        obj = MagicMock()
        obj.pk = None
        obj._meta.model._meta.verbose_name = 'Test Model'
        del obj.breadcrumbs

        breadcrumbs.add_form_breadcrumbs(obj)

        assert len(breadcrumbs) == 2
        assert breadcrumbs.data[0].name == 'Test Model'
        assert breadcrumbs.data[1].name == 'Create'

    def test_add_form_breadcrumbs_edit(self) -> None:
        breadcrumbs = Breadcrumbs()

        obj = MagicMock()
        obj.pk = 1
        del obj.breadcrumbs

        breadcrumbs.add_form_breadcrumbs(obj)

        assert len(breadcrumbs) == 1
        assert breadcrumbs.data[0].name == 'Edit'

    def test_add_obj_breadcrumbs(self) -> None:
        breadcrumbs = Breadcrumbs()

        obj_breadcrumbs = Breadcrumbs()
        obj_breadcrumbs.add_breadcrumb('Object', '/object/')

        obj = MagicMock()
        obj.breadcrumbs.return_value = obj_breadcrumbs

        breadcrumbs.add_obj_breadcrumbs(obj)

        assert len(breadcrumbs) == 1
        assert breadcrumbs.data[0].name == 'Object'

    def test_add_obj_breadcrumbs_no_method(self) -> None:
        breadcrumbs = Breadcrumbs()

        obj = MagicMock(spec=[])

        breadcrumbs.add_obj_breadcrumbs(obj)

        assert len(breadcrumbs) == 0

    def test_add_operator(self) -> None:
        breadcrumbs1 = Breadcrumbs()
        breadcrumbs1.add_breadcrumb('Home', '/home/')

        breadcrumbs2 = Breadcrumbs()
        breadcrumbs2.add_breadcrumb('Page', '/page/')

        result = breadcrumbs1 + breadcrumbs2

        assert len(result) == 2
        assert result.data[0].name == 'Home'
        assert result.data[1].name == 'Page'

    def test_empty_breadcrumbs(self) -> None:
        breadcrumbs = Breadcrumbs()

        assert len(breadcrumbs) == 0

    def test_iteration(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/home/')
        breadcrumbs.add_breadcrumb('Page', '/page/')

        items = list(breadcrumbs)

        assert len(items) == 2
        assert items[0] == {'name': 'Home', 'href': '/home/'}
        assert items[1] == {'name': 'Page', 'href': '/page/'}

    def test_iteration_empty(self) -> None:
        breadcrumbs = Breadcrumbs()

        items = list(breadcrumbs)

        assert items == []

    def test_len(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/home/')
        breadcrumbs.add_breadcrumb('Page', '/page/')

        assert len(breadcrumbs) == 2

    def test_remove(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/home/')
        breadcrumbs.add_breadcrumb('Page', '/page/')
        breadcrumbs.add_breadcrumb('Current', None)

        result = breadcrumbs.remove(1)

        assert len(breadcrumbs) == 2
        assert breadcrumbs.data[0].name == 'Home'
        assert breadcrumbs.data[1].name == 'Current'
        assert result is breadcrumbs

    def test_reverse(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('First', '/first/')
        breadcrumbs.add_breadcrumb('Second', '/second/')
        breadcrumbs.add_breadcrumb('Third', '/third/')

        result = breadcrumbs.reverse()

        assert breadcrumbs.data[0].name == 'Third'
        assert breadcrumbs.data[1].name == 'Second'
        assert breadcrumbs.data[2].name == 'First'
        assert result is breadcrumbs

    def test_str(self) -> None:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb('Home', '/home/')

        result = str(breadcrumbs)

        assert 'BreadcrumbItem' in result or '[' in result

    def test_with_branch_slug(self) -> None:
        breadcrumbs = Breadcrumbs(branch_slug='test-branch')

        assert len(breadcrumbs) == 0
