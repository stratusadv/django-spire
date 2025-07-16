from django import forms

from django_spire.knowledge.collection.models import Collection


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        exclude = []
