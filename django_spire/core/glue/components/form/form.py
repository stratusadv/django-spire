from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue
from django_glue.glue.objects.django.form.object import FormGlue  # noqa: TC002

from django_spire.core.glue.components.form.base import BaseFormComponent

if TYPE_CHECKING:
    from django.forms import BaseForm


class FormComponent(BaseFormComponent):
    """
    A :class:`BaseFormComponent` over a plain form, exposed as the ``form``
    child. Override ``get_form()`` when the form needs constructor arguments
    from the component's parameters.
    """

    @Glue.property
    def form(self) -> FormGlue:
        return Glue.form(target=self.get_form(), access=self.access)

    def get_form(self) -> BaseForm:
        return self.form_class()

    def glue_form_path(self) -> str:
        return 'component.form'
