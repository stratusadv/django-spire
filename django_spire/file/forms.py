from __future__ import annotations

from django import forms

from django_spire.file.fields import MultipleFileField


class FileForm(forms.Form):
    files = MultipleFileField()

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     self.helper = FormHelper(self)
    #     self.helper.include_media = False
    #     self.helper.form_enctype = 'multipart/form-data'
    #     self.helper.layout = Layout(
    #         Row(
    #             Column('files', css_class='form-group col-md-6'),
    #         ),
    #     )
    #     self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
