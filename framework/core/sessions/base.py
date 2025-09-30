from dataclasses import dataclass
from typing import Literal, Dict, Any


State = Literal["created", "active", "errored", "closed"]


@dataclass
class Session:
    id: str
    type: str
    state: State = "created"
    meta: Dict[str, Any] = None

    def open(self):
        self.state = "active"

    def close(self):
        self.state = "closed"