from abc import ABC

from django_spire.core.controllers.controller import BaseController


class BaseViewController(BaseController, ABC):
    pass

class TestViewController(BaseViewController):
    def __init__(self):
        pass