import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4


class SessionStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(exist_ok=True)
        if not self.path.exists():
            self._write({"sessions": []})

    def create(self, type_: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = self._read()
        sid = uuid4().hex[:8]
        sess = {"id": sid, "type": type_, "state": "active", "meta": meta or {}}
        data["sessions"].append(sess)
        self._write(data)
        return sess

    def list(self) -> List[Dict[str, Any]]:
        return self._read()["sessions"]

    def close(self, sid: str) -> bool:
        data = self._read()
        for s in data["sessions"]:
            if s["id"] == sid and s["state"] == "active":
                s["state"] = "closed"
                self._write(data)
                return True
        return False

    def _read(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"sessions": []}

    def _write(self, obj: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(obj), encoding="utf-8")