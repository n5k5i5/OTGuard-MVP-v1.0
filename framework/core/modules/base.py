from abc import ABC, abstractmethod
from typing import Any, Dict


class Module(ABC):
    """Abstract module interface."""

    metadata: Dict[str, Any] = {}

    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def prepare(self, env: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def execute(self, session: Any) -> Dict[str, Any]:
        ...

    def postprocess(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return result

    def teardown(self) -> None:
        pass