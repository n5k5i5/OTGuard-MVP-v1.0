import json
import time
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any


class ReportGate:
    """
    Second-factor gating for report generation.
    Stores a token hash in runs_dir/report_gate.json:

    {
      "enabled": true,
      "token_hash": str,
      "created_at": float
    }
    """

    def __init__(self, runs_dir: Path):
        self.runs_dir = runs_dir
        self.path = self.runs_dir / "report_gate.json"

    def is_enabled(self) -> bool:
        data = self._load() or {}
        return bool(data.get("enabled", True))

    def set_token(self) -> str:
        token = secrets.token_urlsafe(20)
        data = {
            "enabled": True,
            "token_hash": self._hash(token),
            "created_at": time.time(),
        }
        self._save(data)
        return token

    def disable(self) -> None:
        data = self._load() or {}
        data["enabled"] = False
        self._save(data)

    def require(self, token: Optional[str]) -> bool:
        if not self.is_enabled():
            return True
        if not token:
            return False
        data = self._load()
        if not data:
            return False
        expected = data.get("token_hash")
        return bool(expected and expected == self._hash(token))

    # --- helpers ---

    def _load(self) -> Optional[Dict[str, Any]]:
        if not self.path.exists():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _save(self, data: Dict[str, Any]) -> None:
        self.runs_dir.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _hash(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()