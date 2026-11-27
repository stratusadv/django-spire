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

    The data for the child comes from two overridable hooks: ``get_model()``
    picks the instance (blank or fetched by ``model_pk`` by default), and
    ``get_fields()`` names the exposed fields (the form's own fields unless
    ``fields`` is set), so scoping and create defaults stay subclass logic.
    A relation field's choices are the form's own: its ``__init__`` narrows a
    field's queryset, which the form child reads, with the row as
    ``self.instance``.

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
        target = self.get_model()
        initial = self.get_initial()

        if initial:
            form = self.form_class(instance=target, initial=initial)
            form.initial = dict(initial)
        else:
            form = self.form_class

        return Glue.model(
            target=target,
            access=self.access,
            fields=self.get_fields(),
            form=form,
        )

    def get_initial(self) -> dict[str, Any]:
        return {}

    def get_fields(self) -> Sequence[str]:
        if self.fields is None:
            model_field_names = {
                field.name for field in self.form_class._meta.model._meta.get_fields()
            }
            return tuple(name for name in self.form_class.base_fields if name in model_field_names)
        return self.fields

    def get_model(self) -> Model:
        model_class = self.form_class._meta.model
        if self.model_pk is None:
            return model_class()

        try:
            return model_class.objects.get(pk=self.model_pk)
        except model_class.DoesNotExist as error:
            raise GlueModelInstanceNotFoundError(model_class._meta.label, self.model_pk) from error

    def get_permission_model(self) -> type[Model]:
        """Return the form's model, whose permissions ``Glue.ModelAccessMixin`` reads."""
        return self.form_class._meta.model

    def get_required_access(self) -> Glue.Access:
        """``ADD`` to create a row and ``CHANGE`` to edit one, for ``Glue.ModelAccessRequiredMixin``."""
        return Glue.Access.ADD if self.model_pk is None else Glue.Access.CHANGE

    def glue_form_path(self) -> str:
        return 'component.model.form'
