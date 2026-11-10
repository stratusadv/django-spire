from __future__ import annotations

import warnings

from typing import Any, ClassVar, Sequence

from django.db.models import Model  # noqa: TC002
from django.forms import ModelForm
from django_glue import Glue
from django_glue.exceptions import GlueComponentParameterError, GlueModelInstanceNotFoundError

from django_spire.core.components.form.base_component import BaseFormComponent


class ModelFormComponent(BaseFormComponent):
    """
    A :class:`BaseFormComponent` over a ``ModelForm``, whose model is the
    form's own. ``model_pk=None`` opens the create flow and a value opens the
    edit flow. The row is exposed as the ``model`` child, a ``Glue.model``, so
    the form lives at ``component.model.form``.

    The data for the child comes from three overridable hooks: ``get_model()``
    picks the instance (blank or fetched by ``model_pk`` by default),
    ``get_fields()`` names the exposed fields (the form's own fields unless
    ``fields`` is set), and ``get_choices(instance)`` supplies choice
    querysets (none by default), so scoping, create defaults, and
    instance-dependent configuration stay subclass logic.

    ``pk`` is the deprecated name of ``model_pk``, both as a parameter and as
    an attribute.
    """

    form_base = ModelForm
    form_class: ClassVar[type[ModelForm] | None] = None
    fields: ClassVar[Sequence[str] | None] = None

    model_pk: int | None = Glue.ComponentParameter(None)

    def __init__(self, **parameters: Any) -> None:
        if 'pk' in parameters:
            if 'model_pk' in parameters:
                message = f'{type(self).__name__} takes model_pk or the deprecated pk, not both.'
                raise GlueComponentParameterError(message)

            warnings.warn(
                'The pk parameter of ModelFormComponent is deprecated; pass model_pk instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            parameters['model_pk'] = parameters.pop('pk')

        super().__init__(**parameters)

    @property
    def pk(self) -> int | None:
        warnings.warn(
            'ModelFormComponent.pk is deprecated; use model_pk instead.',
            DeprecationWarning,
            stacklevel=2,
        )
        return self.model_pk

    @Glue.child
    def model(self) -> Glue.Model:
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
        if self.model_pk is None:
            return model_class()

        try:
            return model_class.objects.get(pk=self.model_pk)
        except model_class.DoesNotExist as error:
            raise GlueModelInstanceNotFoundError(model_class._meta.label, self.model_pk) from error

    def get_choices(self, _instance: Model) -> dict | None:
        return None

    def glue_form_path(self) -> str:
        return 'component.model.form'
