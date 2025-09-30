import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any


class MetricsCollector:
    def __init__(self, runs_dir: Path):
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(exist_ok=True)

    def start_run(self, kind: str, manifest_id: str, inputs: Dict[str, Any], flags: Dict[str, Any]) -> str:
        run_id = uuid.uuid4().hex[:12]
        path = self._run_path(run_id)
        data = {
            "id": run_id,
            "kind": kind,
            "manifest": manifest_id,
            "inputs": inputs,
            "flags": flags,
            "started_at": time.time(),
            "ended_at": None,
            "success": None,
            "result_summary": None,
            "error": None,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self._set_latest(run_id)
        return run_id

    def end_run(self, run_id: str, success: bool, result_summary: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        path = self._run_path(run_id)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["ended_at"] = time.time()
        data["success"] = success
        data["result_summary"] = result_summary
        data["error"] = error
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def latest_run_id(self) -> Optional[str]:
        latest_file = self.runs_dir / "LATEST"
        if not latest_file.exists():
            return None
        return latest_file.read_text(encoding="utf-8").strip()

    def _set_latest(self, run_id: str):
        latest_file = self.runs_dir / "LATEST"
        latest_file.write_text(run_id, encoding="utf-8")

    def _run_path(self, run_id: str) -> Path:
        return self.runs_dir / f"{run_id}.json"