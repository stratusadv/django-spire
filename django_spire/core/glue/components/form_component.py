from __future__ import annotations

from typing import Any, ClassVar

from django.forms import BaseForm
from django_glue import Glue
from django_glue.glue.objects.django.form.object import FormGlue  # noqa: TC002


def _form_child(self: FormComponent) -> FormGlue:
    return self.build_child()


class FormComponent(Glue.Component):
    """Base for components that expose a single form.

    Subclasses set ``form`` and declare their own construction parameters.
    The form is exposed as a ``Glue.property`` child named by ``attr``, built
    by ``build_child()`` from ``get_form()`` —
    override ``get_form()`` when the form needs constructor arguments from
    the component's parameters. The context carries ``component`` and
    ``glue_form``, the dot path to the form for the template and its
    partials. Whether the component renders in a modal or on a page is a
    template and client-side choice, not part of this base. The class must
    be importable at module level: policy-token reconstruction re-imports it
    by its signed ``module.qualname`` on any worker.
    """

    attr: ClassVar[str]
    form: ClassVar[type[BaseForm]]

    _child_property = _form_child

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if getattr(cls, 'template', None) is None:
            return
        cls._validate_form_configuration()
        setattr(cls, cls.attr, Glue.property(cls._child_property))

    @classmethod
    def _validate_form_configuration(cls) -> None:
        form = getattr(cls, 'form', None)
        if not isinstance(form, type) or not issubclass(form, BaseForm):
            message = f'{cls.__name__}.form must be a form class.'
            raise TypeError(message)
        attr = getattr(cls, 'attr', None)
        if (
            not isinstance(attr, str)
            or not attr.isidentifier()
            or attr.startswith('_')
            or attr == 'pk'
        ):
            message = f'{cls.__name__}.attr must be a public, non-reserved identifier.'
            raise ValueError(message)
        if cls.attr in cls.__dict__:
            message = f'{cls.__name__}.{cls.attr!r} is reserved for the form child.'
            raise ValueError(message)

    def get_form(self) -> BaseForm:
        return self.form()

    def build_child(self) -> FormGlue:
        return Glue.form(target=self.get_form(), access=self.access)

    def glue_form_path(self) -> str:
        return f'component.{self.attr}'

    def get_context_data(self) -> dict[str, Any]:
        return {'component': self, 'glue_form': self.glue_form_path()}
