import platform
import os
from typing import Dict, Any

from framework.core.modules.base import Module


class SysInfoModule(Module):
    metadata = {
        "id": "examples.post.sysinfo",
        "name": "Collect System Info (Example)",
        "version": "0.1.0",
        "type": "post",
        "safety_level": "lab",
    }

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        self.config = {}

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def execute(self, session=None) -> Dict[str, Any]:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cwd": os.getcwd(),
            "env_vars_count": len(os.environ),
        }
        return {"sysinfo": info}