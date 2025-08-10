from django import forms

from django_spire.knowledge.entry.models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ['current_version', 'collection']


class EntryFilesForm(forms.Form):
    collection = forms.IntegerField(required=True)
    import_files = forms.FileField()

    def is_valid(self) -> bool:
        return super().is_valid()
