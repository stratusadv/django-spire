from abc import ABC, abstractmethod


class BaseFileConverter(ABC):
    @abstractmethod
    def convert_to_model_objs(self, file_path: str) -> None:
        raise NotImplementedError
