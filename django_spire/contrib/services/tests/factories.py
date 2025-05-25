from django.contrib.auth.models import User

from django_spire.contrib.services.base_service import BaseService


class UserService(BaseService):

    def __init__(self, user: User):
        self.user = user

