from __future__ import annotations

from abc import ABC, abstractmethod
from importlib import import_module
from typing import Any, ClassVar

from django.core.exceptions import ImproperlyConfigured
from django.forms import BaseForm
from django_glue import Glue


class BaseFormComponent(Glue.Component, ABC):
    """
    Shows one form. The form class and the template are set on a subclass,
    as ``form_class`` and ``template``, or passed when the component is built::

        ModelFormComponent(form_class=TaskForm, template='task/form.html')

    Either way the form class must be importable from its module, because
    the component is rebuilt on each request from its signed path.

    ``glue_form_path()`` is the dot path to the form, read by the template
    and its partials as ``component.glue_form_path``. Whether the component
    is shown in a modal, inline or on a page is the choice of whoever shows it.
    """

    form_base: ClassVar[type[BaseForm]] = BaseForm
    form_class: ClassVar[type[BaseForm] | None] = None

    form_path: str | None = Glue.ComponentParameter(None)
    template_name: str | None = Glue.ComponentParameter(None)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if 'attr' in cls.__dict__:
            message = (
                f'{cls.__name__}.attr was removed: the child is no longer named by attr. '
                'Read the form from glue_form_path().'
            )
            raise TypeError(message)

        if isinstance(cls.__dict__.get('form'), type):
            message = f'{cls.__name__}.form was removed: set the form class as form_class.'
            raise TypeError(message)

        if cls.form_class is not None:
            cls.validate_form_class(cls.form_class)

    def __init__(
        self,
        *,
        form_class: type[BaseForm] | None = None,
        template: str | None = None,
        **kwargs: Any,
    ) -> None:
        if form_class is not None:
            kwargs['form_path'] = f'{form_class.__module__}:{form_class.__qualname__}'

        if template is not None:
            kwargs['template_name'] = template

        if kwargs.get('template_name') is not None:
            self.template = kwargs['template_name']

        super().__init__(**kwargs)

        if self.form_path is not None:
            module_name, _, qualified_name = self.form_path.partition(':')

            try:
                form_class = import_module(module_name)

                for part in qualified_name.split('.'):
                    form_class = getattr(form_class, part)
            except (ImportError, AttributeError) as error:
                message = (
                    f'{type(self).__name__} cannot import its form from {self.form_path!r}: '
                    'the form class must be defined at module level.'
                )
                raise ImproperlyConfigured(message) from error

            self.form_class = form_class

        self.validate_form_class(self.form_class)

    @classmethod
    def validate_form_class(cls, form_class: Any) -> None:
        if not isinstance(form_class, type) or not issubclass(form_class, cls.form_base):
            message = f'{cls.__name__} needs form_class to be a {cls.form_base.__name__} class.'
            raise TypeError(message)

    @abstractmethod
    def glue_form_path(self) -> str:
        """Return the dot path, from the template, to the form this component shows."""
