from __future__ import annotations

from types import SimpleNamespace
from typing import Any, ClassVar, TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from django import forms
from django.db import models
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django_glue import Glue, GlueResponse
from django_glue.glue.event import declared_events
from django_glue.glue.objects.django.form.object import FormGlue
from django_glue.resolver.attribute_call.context import AttributeCallRequestContext

from django_spire import Spire
from django_spire.core.forms import SpireForm, SpireModelForm

if TYPE_CHECKING:
    from django.http import HttpRequest


class ContactForm(Spire.Form):
    email = forms.EmailField()
    note = forms.CharField(required=False)

    def on_submit(self, request: HttpRequest) -> dict[str, Any]:
        return {'email': self.cleaned_data['email'], 'submitted_by': request.user.username}


class CustomResponseForm(Spire.Form):
    title = forms.CharField()

    def on_submit(self, request: HttpRequest) -> GlueResponse:
        _ = request
        return GlueResponse(result={'title': self.cleaned_data['title']})


class FakeModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'django_spire_core'
        managed = False

    def __str__(self) -> str:
        return self.name


class WriteOnlyAndDisabledForm(Spire.Form):
    email = forms.EmailField()
    secret = forms.CharField(widget=forms.PasswordInput())
    locked = forms.CharField(disabled=True, required=False, initial='fixed')

    def on_submit(self, request: HttpRequest) -> dict[str, Any]:
        _ = request
        return {'email': self.cleaned_data['email']}


class FakeModelForm(Spire.ModelForm):
    class Meta:
        model = FakeModel
        fields: ClassVar = ['name']


class ExtraResultModelForm(Spire.ModelForm):
    class Meta:
        model = FakeModel
        fields: ClassVar = ['name']

    def get_submit_result(self, instance: FakeModel) -> dict[str, Any]:
        return {'pk': instance.pk, 'label': instance.name}


class SpireFormTestCase(SimpleTestCase):
    def setUp(self) -> None:
        self.request = RequestFactory().post('/')
        self.request.user = SimpleNamespace(username='alice')
        self.request.session = SimpleNamespace(session_key='test-session')

    def test_spire_namespace_aliases_form_classes(self) -> None:
        assert Spire.Form is SpireForm
        assert Spire.ModelForm is SpireModelForm
        assert issubclass(Spire.ModelForm, Spire.Form)
        assert issubclass(Spire.ModelForm, forms.ModelForm)

        with pytest.raises(AttributeError):
            _ = Spire.NotAForm

    def test_each_subclass_gets_its_own_submitted_event_identity(self) -> None:
        assert ContactForm.submitted is not CustomResponseForm.submitted
        assert FakeModelForm.submitted is not ExtraResultModelForm.submitted
        assert ContactForm.submitted.identity != CustomResponseForm.submitted.identity
        assert dict(declared_events(ContactForm))['submitted'] is ContactForm.submitted
        assert dict(declared_events(FakeModelForm))['submitted'] is FakeModelForm.submitted

    def test_valid_form_submit_returns_result_and_emits_submitted_event(self) -> None:
        glue_form = FormGlue(ContactForm(), name='contact', access=Glue.Access.ADD)
        glue_form.request = self.request

        payload, _introduced = glue_form.process_attribute_call(
            AttributeCallRequestContext.model_construct(
                request=self.request,
                target_glue_policy=glue_form.policy,
                target_glue_updates={'email': 'ada@example.com', 'note': 'hi'},
                target_attribute_name='submit',
                target_attribute_call_kwargs={},
            )
        )

        assert payload['result'] == {'email': 'ada@example.com', 'submitted_by': 'alice'}
        assert payload['effects']['events'] == [
            {'name': 'submitted', 'detail': {'email': 'ada@example.com', 'submitted_by': 'alice'}},
        ]

    def test_invalid_form_submit_returns_error_message_and_field_errors_in_one_call(self) -> None:
        glue_form = FormGlue(ContactForm(), name='contact', access=Glue.Access.ADD)
        glue_form.request = self.request

        payload, _introduced = glue_form.process_attribute_call(
            AttributeCallRequestContext.model_construct(
                request=self.request,
                target_glue_policy=glue_form.policy,
                target_glue_updates={'email': 'not-an-email'},
                target_attribute_name='submit',
                target_attribute_call_kwargs={},
            )
        )

        assert payload['result'] is None
        assert payload['effects']['messages'][0]['message'] == 'Invalid Fields'
        assert payload['effects'].get('events', []) == []
        assert payload['computed_data']['value_attributes']['email']['errors'] == [
            'Enter a valid email address.',
        ]

    def test_invalid_form_submit_syncs_errors_for_untouched_write_only_and_disabled_fields(self) -> None:
        glue_form = FormGlue(WriteOnlyAndDisabledForm(), name='secret_form', access=Glue.Access.ADD)
        glue_form.request = self.request

        payload, _introduced = glue_form.process_attribute_call(
            AttributeCallRequestContext.model_construct(
                request=self.request,
                target_glue_policy=glue_form.policy,
                target_glue_updates={'email': 'not-an-email'},
                target_attribute_name='submit',
                target_attribute_call_kwargs={},
            )
        )

        assert 'secret' in glue_form._derived_paths
        assert 'locked' in glue_form._derived_paths
        assert payload['computed_data']['value_attributes']['secret']['errors'] == [
            'This field is required.',
        ]

    def test_on_submit_returning_glue_response_emits_result_metadata(self) -> None:
        glue_form = FormGlue(CustomResponseForm(), name='custom', access=Glue.Access.ADD)
        glue_form.request = self.request

        payload, _introduced = glue_form.process_attribute_call(
            AttributeCallRequestContext.model_construct(
                request=self.request,
                target_glue_policy=glue_form.policy,
                target_glue_updates={'title': 'Hello'},
                target_attribute_name='submit',
                target_attribute_call_kwargs={},
            )
        )

        assert payload['result'] == {'title': 'Hello'}
        assert payload['effects']['events'] == [
            {'name': 'submitted', 'detail': {'title': 'Hello'}},
        ]

    def test_model_form_uses_service_tuple_return(self) -> None:
        saved_obj = FakeModel(pk=42, name='Alpha')
        instance = FakeModel()
        instance.services = SimpleNamespace(
            save_model_obj=MagicMock(return_value=(saved_obj, True))
        )

        form = FakeModelForm(data={'name': 'Alpha'}, instance=instance)
        response = form.submit(self.request)

        instance.services.save_model_obj.assert_called_once_with(name='Alpha')
        assert response.result == {'pk': 42}

    def test_model_form_uses_service_direct_model_return(self) -> None:
        saved_obj = FakeModel(pk=99, name='Beta')
        instance = FakeModel()
        instance.services = SimpleNamespace(
            save_model_obj=MagicMock(return_value=saved_obj)
        )

        form = ExtraResultModelForm(data={'name': 'Beta'}, instance=instance)
        response = form.submit(self.request)

        assert response.result == {'pk': 99, 'label': 'Beta'}

    def test_model_form_falls_back_to_form_save_without_services(self) -> None:
        saved_obj = FakeModel(pk=7, name='Gamma')
        form = FakeModelForm(data={'name': 'Gamma'})
        form.save = MagicMock(return_value=saved_obj)

        response = form.submit(self.request)

        form.save.assert_called_once_with()
        assert response.result == {'pk': 7}

    def test_form_template_calls_submit_without_redundant_validate(self) -> None:
        html = render_to_string(
            'django_spire/glue/form/form.html',
            {'glue_form_object_name': 'contact_form'},
        )

        assert '.validate()' not in html
        assert 'const form = this.contact_form' in html
        assert "typeof form.submit === 'function' ? 'submit' : 'save_model_obj'" in html
        assert 'finally {' in html
