from abc import ABC, abstractmethod


class BaseBlock(ABC):
    @abstractmethod
    def render_to_markdown(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def render_to_html(self) -> str:
        raise NotImplementedError