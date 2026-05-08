from pydantic import BaseModel, ConfigDict

from dataclasses import dataclass


@dataclass
class CeleryTaskMeta(BaseModel):
    progress: float = 0.0
    remaining_seconds: int = 0

    model_config = ConfigDict(extra='allow')
