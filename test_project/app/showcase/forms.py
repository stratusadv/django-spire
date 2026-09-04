from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from test_project.app.showcase.models import ShowcaseCategory, ShowcaseTag, WidgetShowcase

if TYPE_CHECKING:
    from django.db.models import QuerySet


def _user_choice_queryset() -> QuerySet[User]:
    return Glue.choices(
        User.objects.order_by('username'),
        search_fields=['username', 'first_name', 'last_name'],
        fields=['username', 'first_name', 'last_name'],
    )


class WidgetShowcaseForm(ModelForm):
    # A plain (non-relation) MultipleChoiceField -- glued as ManyChoiceFieldGlue,
    # not ManyRelationFieldGlue. Form-only, not persisted; here so the adaptive
    # multiselect widget is exercised against a static choice source too.
    plain_multi_choice = forms.MultipleChoiceField(
        choices=[('red', 'Red'), ('green', 'Green'), ('blue', 'Blue')],
        required=False,
        label='Plain multi choice',
    )

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self) -> GlueResponse:
        if self.is_valid():
            showcase = self.save()

            return GlueResponse(
                result={'pk': showcase.pk},
                messages=[GlueMessage.success('Widget showcase saved successfully!')],
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields['search_tags'].queryset = Glue.choices(
            ShowcaseTag.objects.order_by('name'), search_fields=['name'], fields=['name']
        )
        self.fields['category'].queryset = Glue.choices(
            ShowcaseCategory.objects.order_by('name'), search_fields=['name'], fields=['name']
        )
        self.fields['assigned_user'].queryset = _user_choice_queryset()
        self.fields['watchers'].queryset = _user_choice_queryset()
        # Deliberately not wrapped in Glue.choices(search_fields=...), unlike
        # 'category' above -- this is what makes choices_searchable False and
        # routes it to select_widget.html instead of search_and_select_widget.html.
        self.fields['primary_category'].queryset = ShowcaseCategory.objects.order_by('name')

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
            'primary_category',
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
