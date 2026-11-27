from __future__ import annotations

from typing import Any, ClassVar, TYPE_CHECKING

from django import forms
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

if TYPE_CHECKING:
    from django.db.models import Model
    from django.http import HttpRequest


class SpireForm(forms.Form):
    invalid_message: ClassVar[str] = 'Invalid Fields'
    submitted = Glue.event()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if 'submitted' not in cls.__dict__:
            event = Glue.event()
            event.__set_name__(cls, 'submitted')
            cls.submitted = event

    @Glue.attribute(required_access=Glue.Access.required_save_access)
    def submit(self, request: HttpRequest) -> GlueResponse:
        if not self.is_valid():
            return self.on_invalid(request)

        response = self.on_submit(request)

        if not isinstance(response, GlueResponse):
            response = GlueResponse(result=response)

        detail = response.result if isinstance(response.result, dict) else {}
        self.submitted(**detail)

        return response

    def on_invalid(self, request: HttpRequest) -> GlueResponse:
        _ = request
        glue_owner = getattr(self, '_glue_event_owner', None)

        if glue_owner is not None:
            derived_paths = getattr(glue_owner, '_derived_paths', None)

            if isinstance(derived_paths, set):
                derived_paths.update(self.fields)

        return GlueResponse(messages=[GlueMessage.error(self.invalid_message)])

    def on_submit(self, request: HttpRequest) -> GlueResponse | dict[str, Any] | None:
        _ = request
        raise NotImplementedError


class SpireModelForm(SpireForm, forms.ModelForm):
    def on_submit(self, request: HttpRequest) -> GlueResponse | dict[str, Any]:
        instance = self.save_instance(request)
        return self.get_submit_result(instance)

    def save_instance(self, request: HttpRequest) -> Model:
        _ = request
        services = getattr(self.instance, 'services', None)

        if services is not None and hasattr(services, 'save_model_obj'):
            saved_instance = services.save_model_obj(**self.cleaned_data)
            return saved_instance[0] if isinstance(saved_instance, tuple) else saved_instance

        return self.save()

    def get_submit_result(self, instance: Model) -> dict[str, Any]:
        return {'pk': instance.pk}
