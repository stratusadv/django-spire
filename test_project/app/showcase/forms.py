from __future__ import annotations

from typing import TYPE_CHECKING

from django.forms import ModelForm
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from test_project.app.showcase.models import WidgetShowcase

if TYPE_CHECKING:
    from django.http import HttpRequest


class WidgetShowcaseForm(ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            showcase = self.save()

            return GlueResponse(
                result={'pk': showcase.pk},
                messages=[GlueMessage.success('Widget showcase saved successfully!')],
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = WidgetShowcase
        fields = [
            'boolean_field',
            'char_field',
            'color_field',
            'email_field',
            'password_field',
            'postal_code_field',
            'search_field',
            'slug_field',
            'telephone_field',
            'url_field',
            'uuid_field',
            'select_choice',
            'checkbox_tags',
            'search_tags',
            'radio_choice',
            'category',
            'watchers',
            'assigned_user',
            'date_field',
            'datetime_field',
            'time_field',
            'currency_field',
            'decimal_field',
            'float_field',
            'hidden_field',
            'big_integer_field',
            'integer_field',
            'positive_integer_field',
            'small_integer_field',
            'text_field',
        ]
