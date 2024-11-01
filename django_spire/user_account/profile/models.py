from dateutil import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime

from django_spire.history.mixins import HistoryModelMixin
from django_spire.permission.models import PortalUser
from django_spire.user_account.mixins import UserOptionsModelMixin


class UserProfile(HistoryModelMixin, UserOptionsModelMixin):
    user = models.OneToOneField(
        PortalUser,
        on_delete=models.CASCADE,
        related_name='profile',
        related_query_name='profile'
    )

    mfa_valid_till_datetime = models.DateTimeField(default=localtime, editable=False)

    def __str__(self):
        return self.user.username

    def requires_mfa(self):
        return self.mfa_valid_till_datetime < localtime()

    def set_mfa_grace_period(self):
        self.mfa_valid_till_datetime = localtime() + relativedelta.relativedelta(hours=24)
        self.save()

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'spire_user_account_profile'


@receiver(post_save, sender=PortalUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    from django_spire.user_account.factories import create_user_profile

    if created:
        create_user_profile(instance)

    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        create_user_profile(instance)
