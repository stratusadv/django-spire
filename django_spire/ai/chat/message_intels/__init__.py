from abc import ABC

from dandy.intel import BaseIntel
from pydantic.fields import PrivateAttr


class BaseMessageIntel(BaseIntel, ABC):
    _template: str = PrivateAttr(default_factory=str)
