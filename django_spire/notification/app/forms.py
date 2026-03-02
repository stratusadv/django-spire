from django import forms


class NotificationListFilterForm(forms.Form):
    search = forms.CharField(required=False)
