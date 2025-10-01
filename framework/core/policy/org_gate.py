import json
import time
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any


class OrgGate:
    """
    Company/organization approval gate.
    Stores state in runs_dir/org.json with fields:
    {
      "name": str,
      "domain": str,
      "email": str,
      "status": "pending"|"verified",
      "token_hash": str,
      "created_at": float,
      "verified_at": float|None
    }
    """

    def __init__(self, runs_dir: Path, emailer=None, webhook=None):
        self.runs_dir = runs_dir
        self.path = self.runs_dir / "org.json"
        self.emailer = emailer
        self.webhook = webhook

    def is_verified(self) -> bool:
        data = self._load()
        return bool(data and data.get("status") == "verified")

    def status(self) -> Dict[str, Any]:
        data = self._load() or {}
        redacted = dict(data)
        if "token_hash" in redacted:
            redacted["token_hash"] = "***"
        return redacted

    def init_org(self, name: str, domain: str, email: str) -> str:
        token = self._generate_token()
        token_hash = self._hash(token)
        data = {
            "name": name,
            "domain": domain,
            "email": email,
            "status": "pending",
            "token_hash": token_hash,
            "created_at": time.time(),
            "verified_at": None,
        }
        self._save(data)
        # send notification
        if self.emailer is not None:
            try:
                self.emailer.send_verification(email, name, token)
            except Exception:
                # fail-closed: do not verify automatically; token can be used via CLI
                pass
        if getattr(self, "webhook", None) is not None:
            try:
                self.webhook.notify_verification(name, domain, email, token)
            except Exception:
                pass
        return token

    def verify(self, token: str) -> bool:
        data = self._load()
        if not data:
            return False
        expected = data.get("token_hash")
        if expected and secrets.compare_digest(expected, self._hash(token)):
            data["status"] = "verified"
            data["verified_at"] = time.time()
            self._save(data)
            return True
        return False

    def reset(self) -> None:
        if self.path.exists():
            self.path.unlink()

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
    def _generate_token() -> str:
        return secrets.token_urlsafe(20)

    @staticmethod
    def _hash(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()