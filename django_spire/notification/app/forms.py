from django import forms


class NotificationListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    status = forms.CharField(required=False)
    priority = forms.CharField(required=False)
