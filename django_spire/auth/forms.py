from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class CaseInsensitiveAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get("username")

        if username:
            user = User.objects.filter(
                username__iexact=username.lower()
            ).first()

            if user is None:
                raise self.get_invalid_login_error()

            self.cleaned_data["username"] = user.username

        return super().clean()

