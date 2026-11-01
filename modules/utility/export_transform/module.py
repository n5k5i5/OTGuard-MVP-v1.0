import csv
import json
from pathlib import Path
from typing import Dict, Any

from framework.core.modules.base import Module


class ExportTransformModule(Module):
    metadata = {
        "id": "util.transform.export",
        "name": "Assessment Results Exporter (JSON/CSV)",
        "version": "1.0.0",
        "type": "aux",
        "safety_level": "lab",
    }

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        if "data" not in config:
            raise ValueError("data input is required")
        fmt = str(config.get("format", "json")).lower()
        if fmt not in ("json", "csv"):
            raise ValueError("format must be 'json' or 'csv'")
        out_file = config.get("output_file", ".runs/assessment_export.json")
        self.config = {
            "data": config["data"],
            "format": fmt,
            "output_file": str(out_file),
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def execute(self, session=None) -> Dict[str, Any]:
        data = self.config["data"]
        fmt = self.config["format"]
        out_path = Path(self.config["output_file"])
        out_path.parent.mkdir(parents=True, exist_ok=True)

        count = len(data) if isinstance(data, (list, dict)) else 1

        if fmt == "json":
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif fmt == "csv":
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Target/Key", "Value"])
                if isinstance(data, dict):
                    for k, v in data.items():
                        writer.writerow([k, json.dumps(v, ensure_ascii=False)])
                elif isinstance(data, list):
                    for idx, row in enumerate(data):
                        writer.writerow([idx, json.dumps(row, ensure_ascii=False)])

        return {
            "exported_path": str(out_path),
            "record_count": count,
            "format": fmt,
        }
