# from captcha.fields import ReCaptchaField
# from captcha.widgets import ReCaptchaV2Checkbox
# from django import forms
#
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Row, Column, HTML
#
#
# SUBJECT_TOPIC_CHOICES = (
#     ('aaa', 'Example_1'),
#     ('bbb', 'Example_2'),
#     ('ccc', 'Example_3'),
#     ('ddd', 'Example_4'),
#     ('oth', 'Other'),
# )
#
#
# class ContactUsForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         super(ContactUsForm, self).__init__(*args, **kwargs)
#
#         self.fields['name'] = forms.CharField(max_length=124)
#         self.fields['company'] = forms.CharField(max_length=124)
#         self.fields['email'] = forms.EmailField()
#         self.fields['inquiry'] = forms.ChoiceField(choices=SUBJECT_TOPIC_CHOICES)
#         self.fields['message'] = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}))
#         self.fields['captcha'] = ReCaptchaField(widget=ReCaptchaV2Checkbox)
#
#         self.helper = FormHelper(self)
#         self.helper.include_media = False
#
#         self.helper.layout = Layout(
#             Row(
#                 Column('name', css_class='form-group col-12'),
#                 Column('company', css_class='form-group col-12'),
#                 Column('email', css_class='form-group col-12'),
#                 Column('inquiry', css_class='form-group col-12'),
#                 Column('message', css_class='form-group col-12'),
#             ),
#             Row(
#                 Column('captcha', css_class='form-group col-12'),
#             ),
#
#             HTML("{% include 'core/element/form_button_element.html' %}"),
#         )
