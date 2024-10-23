from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django import forms


class MFAForm(forms.Form):
    def __init__(self, generated_mfa_code, *args, **kwargs):
        super(MFAForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.generated_mfa_code = generated_mfa_code
        self.fields['mfa_code'] = forms.CharField(max_length=6, label='Authentication Code')

        self.helper.layout = Layout(
            Row(
                Column('mfa_code', css_class='form-group col-12'),
            ),
            HTML("{% include 'core/form/form_submit_button.html' %}")
        )

    def clean(self):
        cleaned_data = super(MFAForm, self).clean()
        mfa_code = cleaned_data.get('mfa_code')
        if mfa_code != self.generated_mfa_code.code:
            self.add_error('mfa_code', 'Invalid MFA Code.')