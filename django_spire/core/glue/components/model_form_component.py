from __future__ import annotations

from typing import Any, ClassVar, Sequence

from django.db.models import Model
from django.forms import ModelForm  # noqa: TC002
from django_glue import Glue
from django_glue.glue.objects.django.model.object import ModelGlue  # noqa: TC002

from django_spire.core.glue.components.form_component import FormComponent


def _model_child(self: ModelFormComponent) -> ModelGlue:
    return self.build_child()


class ModelFormComponent(FormComponent):
    """A :class:`FormComponent` bound to a model's form.

    Subclasses set ``model_class`` and ``fields`` (or override
    ``get_fields()``) on top of the form base. ``pk`` is declared here —
    ``pk=None`` opens the create flow, a value opens the edit flow — and the
    child is a ``Glue.model`` named by ``attr`` (default ``model``), so the
    form lives at ``component.<attr>.form``.

    The data for the child comes from three overridable hooks: ``get_model()``
    picks the instance (blank or fetched by ``pk`` by default),
    ``get_fields()`` names the exposed fields (``fields`` by default), and
    ``get_choices(instance)`` supplies choice querysets (none by default), so
    scoping, create defaults, and instance-dependent configuration stay
    subclass logic.
    """

    attr: ClassVar[str] = 'model'
    model_class: ClassVar[type[Model]]
    form: ClassVar[type[ModelForm]]
    fields: ClassVar[Sequence[str]]

    _child_property = _model_child

    pk: int | None = Glue.ComponentParameter(None)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if getattr(cls, 'template', None) is None:
            return
        cls._validate_model_configuration()

    @classmethod
    def _validate_model_configuration(cls) -> None:
        model_class = getattr(cls, 'model_class', None)
        if not isinstance(model_class, type) or not issubclass(model_class, Model):
            message = f'{cls.__name__}.model_class must be a model class.'
            raise TypeError(message)
        if not getattr(cls, 'fields', None) and cls.get_fields is ModelFormComponent.get_fields:
            message = f'{cls.__name__} must define fields or override get_fields().'
            raise ValueError(message)

    def get_fields(self) -> Sequence[str]:
        return self.fields

    def get_model(self) -> Model:
        if self.pk is None:
            return self.model_class()
        return self.model_class.objects.get(pk=self.pk)

    def get_choices(self, _instance: Model) -> dict | None:
        return None

    def build_child(self) -> ModelGlue:
        instance = self.get_model()
        options: dict[str, Any] = {
            'target': instance,
            'access': self.access,
            'fields': self.get_fields(),
            'form': self.form,
        }
        choices = self.get_choices(instance)
        if choices is not None:
            options['choices'] = choices
        return Glue.model(**options)

    def glue_form_path(self) -> str:
        return f'component.{self.attr}.form'
