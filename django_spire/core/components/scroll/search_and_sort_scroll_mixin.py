from __future__ import annotations

from typing import Any, ClassVar

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django_glue import Glue


class SearchAndSortScrollMixin:
    """
    Adds ``search`` and optional ``sort`` :class:`Glue.ComponentField`
    attributes to a scroll component without writing a boilerplate
    ``FilterForm``.

    Declare ``default_sort`` as a Django ``Choices`` member (e.g.
    ``SolutionSortChoices.NAME``) and ``sort_choices`` is inferred from
    ``type(default_sort)`` automatically. Or declare ``sort_choices`` alone to
    default to its first choice. Omit both for a search-only list.
    """

    sort_choices: ClassVar[type[models.Choices] | None] = None
    default_sort: ClassVar[models.Choices | str | None] = None

    search: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if issubclass(cls, Glue.Component) and not any(
            'search' in base.__dict__ for base in cls.__mro__
        ):
            search_declaration = Glue.ComponentField(forms.CharField(required=False))
            search_declaration.__set_name__(cls, 'search')
            cls.search = search_declaration

        own_sort_choices = cls.__dict__.get('sort_choices')
        own_default_sort = cls.__dict__.get('default_sort')

        if own_sort_choices is None and isinstance(own_default_sort, models.Choices):
            cls.sort_choices = type(own_default_sort)
        elif cls.sort_choices is None and cls.default_sort is not None:
            if isinstance(cls.default_sort, models.Choices):
                cls.sort_choices = type(cls.default_sort)
            else:
                message = (
                    f'{cls.__name__}.default_sort must be a Django Choices member '
                    'when sort_choices is not set.'
                )
                raise ImproperlyConfigured(message)

        has_inherited_sort = any('sort' in base.__dict__ for base in cls.__mro__)

        if issubclass(cls, Glue.Component) and cls.sort_choices is not None and (
            'sort' not in cls.__dict__
            and (not has_inherited_sort or own_sort_choices is not None or own_default_sort is not None)
        ):
            if not (isinstance(cls.sort_choices, type) and issubclass(cls.sort_choices, models.Choices)):
                message = f'{cls.__name__}.sort_choices must be a Django Choices subclass.'
                raise ImproperlyConfigured(message)

            if cls.default_sort is not None:
                try:
                    initial = cls.sort_choices(cls.default_sort)
                except ValueError as error:
                    message = (
                        f'{cls.__name__}.default_sort ({cls.default_sort!r}) is not a valid '
                        f'{cls.sort_choices.__name__} choice.'
                    )
                    raise ImproperlyConfigured(message) from error
            else:
                initial = cls.sort_choices(cls.sort_choices.choices[0][0])

            sort_declaration = Glue.ComponentField(
                forms.TypedChoiceField(
                    choices=cls.sort_choices.choices,
                    coerce=cls.sort_choices,
                    initial=initial,
                )
            )
            sort_declaration.__set_name__(cls, 'sort')
            cls.sort = sort_declaration

        super().__init_subclass__(**kwargs)
