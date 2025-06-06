from abc import ABC, abstractmethod

from django_spire.core.controllers import BaseViewController
from django_spire.core.controllers.controller import BaseController


class BaseUrlController(BaseController, ABC):
    @abstractmethod
    def __init__(self, view_controller: BaseViewController):
        raise NotImplementedError