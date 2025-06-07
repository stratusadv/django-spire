from django.contrib.auth.models import User

from django_spire.contrib.service.service import BaseService


class UserService(BaseService):
    obj_class = User
    obj_name = 'user'



class UserSubService(BaseService):
    obj_class = User
    obj_name = 'user'

