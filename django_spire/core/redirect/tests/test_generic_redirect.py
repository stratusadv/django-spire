from __future__ import annotations

import pytest

from unittest.mock import MagicMock

from django.test import TestCase

from django_spire.core.redirect.generic_redirect import reverse_generic_relation


class TestReverseGenericRelation(TestCase):
    def test_model_not_in_map_raises_key_error(self) -> None:
        """
        Since CONTENT_OBJECT_URL_MAP is empty by default,
        any model lookup raises KeyError.
        """

        content_object = MagicMock()
        content_object.__class__.__name__ = 'UnknownModel'

        with pytest.raises(KeyError):
            reverse_generic_relation(content_object)

    def test_uses_lowercase_model_name(self) -> None:
        """Verifies the model name is lowercased for map lookup."""

        content_object = MagicMock()
        content_object.__class__.__name__ = 'MyModel'

        with pytest.raises(KeyError) as exc_info:
            reverse_generic_relation(content_object)

        assert exc_info.value.args[0] == 'mymodel'
