import json
import time
from pathlib import Path
from typing import Any, Dict


class AppLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(exist_ok=True)

    def log(self, event: str, data: Dict[str, Any] | None = None) -> None:
        record = {
            "ts": time.time(),
            "event": event,
            "data": data or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")