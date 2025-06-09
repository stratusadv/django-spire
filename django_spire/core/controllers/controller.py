from abc import ABC


class BaseController(ABC):
    pass
# name_space: str
    #
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__()
    #     if not hasattr(cls, 'name_space'):
    #         raise ValueError('The controller must have a "name_space" attribute')