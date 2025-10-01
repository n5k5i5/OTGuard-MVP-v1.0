import json
import time
from pathlib import Path
from typing import Any, Dict


class AppLogger:
    def __init__(self, path: Path):
        """
        Initialize the logger with the target log file path.
        
        Parameters:
            path (Path): Filesystem path for the JSON Lines log file. The parent directory will be created if it does not exist.
        """
        self.path = path
        self.path.parent.mkdir(exist_ok=True)

    def log(self, event: str, data: Dict[str, Any] | None = None) -> None:
        """
        Append a JSON-encoded log record with a timestamp, event name, and optional data to the configured file.
        
        Parameters:
            event (str): Name of the event to record.
            data (Dict[str, Any] | None): Optional additional information to include in the record; treated as an empty dict if None.
        
        Notes:
            The record written contains keys "ts" (timestamp), "event", and "data", and is written as a single JSON line to the logger's path.
        """
        record = {
            "ts": time.time(),
            "event": event,
            "data": data or {},
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")