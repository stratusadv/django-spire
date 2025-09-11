from django.contrib.auth.models import Group
from django_spire.auth.user.models import AuthUser


def add_user_to_all_user_group(user: AuthUser):
    try:
        all_user_group = Group.objects.get(name='All Users')
    except Group.DoesNotExist:
        all_user_group = Group.objects.create(name='All Users')

    all_user_group.user_set.add(user)
