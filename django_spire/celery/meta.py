from pydantic import BaseModel, ConfigDict


class CeleryTaskMeta(BaseModel):
    progress: float = 0.0
    remaining_seconds: int = -1

    model_config = ConfigDict(extra='allow')
