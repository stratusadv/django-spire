from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured

from django_spire.core.components import (
    BaseConfirmationComponent,
    ComponentDeleteOptions,
    ModelDeleteConfirmationComponent,
    ModelSetDeletedConfirmationComponent,
    PageDeleteOptions,
)
from django_spire.core.tests.test_cases import BaseTestCase


class ComponentDeleteOptionsTestCase(BaseTestCase):
    def test_the_confirmation_soft_deletes_unless_another_is_given(self) -> None:
        assert ComponentDeleteOptions().component is ModelSetDeletedConfirmationComponent
        assert (
            ComponentDeleteOptions(component=ModelDeleteConfirmationComponent).component
            is ModelDeleteConfirmationComponent
        )

    def test_a_component_that_is_not_a_delete_confirmation_is_refused(self) -> None:
        with pytest.raises(ImproperlyConfigured, match='BaseModelDeleteConfirmationComponent'):
            ComponentDeleteOptions(component=BaseConfirmationComponent)

        with pytest.raises(ImproperlyConfigured, match='BaseModelDeleteConfirmationComponent'):
            ComponentDeleteOptions(component='order:delete')


class PageDeleteOptionsTestCase(BaseTestCase):
    def test_the_return_route_is_optional(self) -> None:
        returning = PageDeleteOptions('order:delete', return_url_name='order:list')

        assert PageDeleteOptions('order:delete').return_url_name is None
        assert (returning.url_name, returning.return_url_name) == ('order:delete', 'order:list')
