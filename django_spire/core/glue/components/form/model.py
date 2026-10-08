from __future__ import annotations

from typing import Any, ClassVar, Sequence

from django.db.models import Model  # noqa: TC002
from django.forms import ModelForm
from django_glue import Glue
from django_glue.glue.objects.django.model.object import ModelGlue  # noqa: TC002

from django_spire.core.glue.components.form.base import BaseFormComponent


class ModelFormComponent(BaseFormComponent):
    """
    A :class:`BaseFormComponent` over a ``ModelForm``, whose model is the
    form's own. ``pk=None`` opens the create flow and a value opens the edit
    flow. The row is exposed as the ``model`` child, a ``Glue.model``, so the
    form lives at ``component.model.form``.

    The data for the child comes from three overridable hooks: ``get_model()``
    picks the instance (blank or fetched by ``pk`` by default),
    ``get_fields()`` names the exposed fields (the form's own fields unless
    ``fields`` is set), and ``get_choices(instance)`` supplies choice
    querysets (none by default), so scoping, create defaults, and
    instance-dependent configuration stay subclass logic.
    """

    form_base = ModelForm
    form_class: ClassVar[type[ModelForm] | None] = None
    fields: ClassVar[Sequence[str] | None] = None

    pk: int | None = Glue.ComponentParameter(None)

    @Glue.property
    def model(self) -> ModelGlue:
        instance = self.get_model()
        options: dict[str, Any] = {
            'target': instance,
            'access': self.access,
            'fields': self.get_fields(),
            'form': self.form_class,
        }
        choices = self.get_choices(instance)
        if choices is not None:
            options['choices'] = choices
        return Glue.model(**options)

    def get_fields(self) -> Sequence[str]:
        if self.fields is None:
            return tuple(self.form_class.base_fields)
        return self.fields

    def get_model(self) -> Model:
        model_class = self.form_class._meta.model
        if self.pk is None:
            return model_class()
        return model_class.objects.get(pk=self.pk)

    def get_choices(self, _instance: Model) -> dict | None:
        return None

    def glue_form_path(self) -> str:
        return 'component.model.form'
