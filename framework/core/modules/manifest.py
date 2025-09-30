from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any


@dataclass
class ModuleManifest:
    path: Path
    data: Dict[str, Any]

    @property
    def id(self) -> str:
        return self.data.get("id", "")

    def __getitem__(self, item):
        return self.data[item]

    def get(self, key, default=None):
        return self.data.get(key, default)