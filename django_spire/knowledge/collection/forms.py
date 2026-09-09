from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from django import forms
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.auth.group.models import AuthGroup
from django_spire.knowledge.collection.models import Collection, CollectionGroup

if TYPE_CHECKING:
    from django.http import HttpRequest


class CollectionForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=AuthGroup.objects.none(), required=False, label='Groups'
    )

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if not self.is_valid():
            return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

        field_data = dict(self.cleaned_data)
        groups = field_data.pop('groups')

        collection, _created = self.instance.services.save_model_obj(**field_data)

        CollectionGroup.services.factory.replace_groups(
            request=request,
            group_pks=list(groups.values_list('pk', flat=True)),
            collection=collection,
        )

        collection.services.tag.process_and_set_tags()

        if collection.parent_id:
            return_url = reverse(
                'django_spire:knowledge:collection:page:top_level',
                kwargs={'pk': collection.parent_id},
            )
        else:
            return_url = reverse('django_spire:knowledge:page:home')

        return GlueResponse(result={'redirect': {'url': return_url}})

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields['groups'].queryset = Glue.choices(
            AuthGroup.objects.all().order_by('name'), fields=['name']
        )

        if self.instance.pk:
            self.fields['groups'].initial = list(
                self.instance.groups.values_list('auth_group_id', flat=True)
            )

    class Meta:
        model = Collection
        fields: ClassVar[list] = ['parent', 'name', 'description']
