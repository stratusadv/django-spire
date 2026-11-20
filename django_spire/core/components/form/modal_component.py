from __future__ import annotations

from django.utils.text import capfirst
from django_glue import Glue

from django_spire.core.components.form.model_component import ModelFormComponent


class ModalModelFormComponent(ModelFormComponent):
    """
    A :class:`ModelFormComponent` shown in a modal that Spire draws: a header
    titled "New Task" or "Edit Task" from the model's ``verbose_name``, and a
    body that includes ``form_template``, the partial with the form's fields.
    """

    template = 'django_spire/component/form/modal_form.html'

    form_template: str = Glue.ComponentParameter()

    @property
    def modal_title(self) -> str:
        action = 'New' if self.model_pk is None else 'Edit'
        return f'{action} {capfirst(self.form_class._meta.model._meta.verbose_name)}'
