import json
import time
import uuid
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any


class MetricsCollector:
    def __init__(self, runs_dir: Path):
        """
        Initialize the MetricsCollector with a directory for run data and prepare persistent storage.
        
        Ensures the provided directory exists, sets the path for the SQLite metrics database, and initializes the database schema used to persist run records.
        
        Parameters:
            runs_dir (Path): Directory where per-run JSON files and the SQLite metrics database (metrics.db) are stored.
        """
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(exist_ok=True)
        # initialize sqlite store
        self._db_path = self.runs_dir / "metrics.db"
        self._db_init()

    def start_run(self, kind: str, manifest_id: str, inputs: Dict[str, Any], flags: Dict[str, Any]) -> str:
        """
        Create a new run record and persist its initial metadata.
        
        Persists the run's metadata to a JSON file and the internal SQLite database, and updates the LATEST pointer to this run.
        
        Parameters:
            kind (str): Logical category or type of the run.
            manifest_id (str): Identifier of the manifest associated with the run.
            inputs (Dict[str, Any]): Input values provided to the run.
            flags (Dict[str, Any]): Runtime flags or options applied to the run.
        
        Returns:
            str: A 12-character hexadecimal run identifier.
        """
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
        self._db_insert_start(data)
        self._set_latest(run_id)
        return run_id

    def end_run(self, run_id: str, success: bool, result_summary: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """
        Mark a run as finished and persist its final metadata.
        
        Updates the run's JSON file to set the completion timestamp, success flag, result summary, and error message, and updates the corresponding database record.
        
        Parameters:
            run_id (str): Identifier of the run to end.
            success (bool): Whether the run completed successfully.
            result_summary (Optional[Dict[str, Any]]): Structured summary of the run result, if any.
            error (Optional[str]): Error message or details if the run failed.
        """
        path = self._run_path(run_id)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["ended_at"] = time.time()
        data["success"] = success
        data["result_summary"] = result_summary
        data["error"] = error
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self._db_update_end(data)

    def latest_run_id(self) -> Optional[str]:
        """
        Get the most recently started run's ID as recorded in the runs directory.
        
        Reads the LATEST file in the runs directory and returns its contents with surrounding whitespace removed.
        
        Returns:
            str: Run ID from the LATEST file, or `None` if the LATEST file does not exist.
        """
        latest_file = self.runs_dir / "LATEST"
        if not latest_file.exists():
            return None
        return latest_file.read_text(encoding="utf-8").strip()

    def _set_latest(self, run_id: str):
        """
        Record the given run ID as the latest run by writing it to the LATEST pointer file in the runs directory.
        
        Parameters:
            run_id (str): The run identifier to store in the LATEST file.
        """
        latest_file = self.runs_dir / "LATEST"
        latest_file.write_text(run_id, encoding="utf-8")

    def _run_path(self, run_id: str) -> Path:
        """
        Compute the filesystem path for the JSON file associated with a run.
        
        Parameters:
            run_id (str): The run identifier used as the filename base (without extension).
        
        Returns:
            Path: Path to the run's JSON file located in the collector's runs directory.
        """
        return self.runs_dir / f"{run_id}.json"

    # --- SQLite helpers ---

    def _db_init(self) -> None:
        """
        Ensure the SQLite database at self._db_path contains the required runs table.
        
        Creates the `runs` table if it does not already exist. The table schema includes
        the following columns: `id` (TEXT PRIMARY KEY), `kind` (TEXT), `manifest` (TEXT),
        `started_at` (REAL), `ended_at` (REAL), `success` (INTEGER), `flags` (TEXT),
        `inputs` (TEXT), `result_summary` (TEXT), and `error` (TEXT). The database file
        is created if it does not exist.
        """
        con = sqlite3.connect(self._db_path)
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY,
                    kind TEXT,
                    manifest TEXT,
                    started_at REAL,
                    ended_at REAL,
                    success INTEGER,
                    flags TEXT,
                    inputs TEXT,
                    result_summary TEXT,
                    error TEXT
                )
                """
            )
            con.commit()
        finally:
            con.close()

    def _db_insert_start(self, data: Dict[str, Any]) -> None:
        """
        Insert or replace a row in the metrics SQLite database to record the start of a run.
        
        Parameters:
            data (Dict[str, Any]): Run metadata containing at least the keys:
                - id: run identifier
                - kind: run kind
                - manifest: manifest identifier
                - started_at: start timestamp
                Optional keys:
                - flags: mapping of flag names to values (will be JSON-serialized)
                - inputs: mapping of input names to values (will be JSON-serialized)
        
        Description:
            Serializes `flags` and `inputs` to JSON and inserts or replaces a row in the `runs`
            table with the provided start values. The columns `ended_at`, `success`,
            `result_summary`, and `error` are stored as NULL for a run start. The change is
            committed to the database before the connection is closed.
        """
        con = sqlite3.connect(self._db_path)
        try:
            con.execute(
                "INSERT OR REPLACE INTO runs (id, kind, manifest, started_at, ended_at, success, flags, inputs, result_summary, error) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    data["id"],
                    data["kind"],
                    data["manifest"],
                    data["started_at"],
                    None,
                    None,
                    json.dumps(data.get("flags", {})),
                    json.dumps(data.get("inputs", {})),
                    None,
                    None,
                ),
            )
            con.commit()
        finally:
            con.close()

    def _db_update_end(self, data: Dict[str, Any]) -> None:
        """
        Update the SQLite runs row for a completed run with end metadata.
        
        Updates the row in the runs table identified by data['id'], setting ended_at, success (1 if true, 0 otherwise), result_summary (stored as JSON), and error.
        
        Parameters:
            data (Dict[str, Any]): Run metadata containing:
                - id (str): Identifier of the run to update.
                - ended_at: Timestamp when the run ended.
                - success (bool): Whether the run succeeded.
                - result_summary: Object summarizing the run result (will be JSON-serialized).
                - error (Optional[str]): Error message if the run failed.
        """
        con = sqlite3.connect(self._db_path)
        try:
            con.execute(
                "UPDATE runs SET ended_at = ?, success = ?, result_summary = ?, error = ? WHERE id = ?",
                (
                    data.get("ended_at"),
                    1 if data.get("success") else 0,
                    json.dumps(data.get("result_summary")),
                    data.get("error"),
                    data["id"],
                ),
            )
            con.commit()
        finally:
            con.close()