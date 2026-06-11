from abc import ABC, abstractmethod
from typing import Any


class PipelineStep(ABC):
    @abstractmethod
    def execute(self, data: Any, context: dict = None) -> Any:
        pass

    def validate(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
