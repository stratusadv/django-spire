from django.contrib.auth.models import User

from django_spire.contrib.service.service import BaseService


class UserService(BaseService):

    def __init__(self, user: User):
        self.user = user

