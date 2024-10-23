import random
from dateutil import relativedelta

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.timezone import localtime

from django_spire.core.notification.models import Notification
from django_spire.core.notification.sender import SendGridEmailHelper
from django_spire.history.mixins import HistoryModelMixin
from django_spire.user_account.authentication.mfa.querysets import MfaCodeQuerySet


class MfaCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_query_name='mfa_code', related_name='mfa_codes')
    code = models.CharField(max_length=6, editable=False, unique=True)
    expiration_datetime = models.DateTimeField(editable=False)

    objects = MfaCodeQuerySet.as_manager()

    def __str__(self):
        return f'{self.expiration_datetime} - {self.code}'

    def is_valid(self):
        return self.expiration_datetime > localtime()

    def set_expired(self):
        self.expiration_datetime = localtime()
        self.save()

    def send_notification(self):
        user = self.user
        context_data = {
            'title': 'Authentication Code',
            'body': f"Here is your multifactor authentication code: </br> <h3>{self.code}</h3>",
            'name': user.first_name,
            'button_url': f'{Site.objects.get_current()}/{reverse("user_account:authentication:redirect:login_redirect")[1:]}'
        }

        # Directly connecting to sendgrid to send MFA email faster
        SendGridEmailHelper(
            to=[user.email],
            template_id='d-9ae6be6be95d4f79b0daad9055f03cc9',
            template_data=context_data,
            fail_silently=False
        ).send()

    @classmethod
    def generate_code(cls, user):
        return MfaCode.objects.create(
            user=user,
            code=int(''.join([str(random.randint(0, 9)) for _ in range(6)])),
            expiration_datetime=localtime() + relativedelta.relativedelta(minutes=5)
        )

    class Meta:
        db_table = 'authentication_mfa_code'
