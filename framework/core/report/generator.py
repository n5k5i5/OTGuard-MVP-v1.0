import json
from pathlib import Path
from typing import Any, List


class ReportGenerator:
    def __init__(self, runs_dir: Path):
        self.runs_dir = runs_dir

    def generate_html(self, run_id: str) -> Path:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Run not found: {run_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        html = self._render_html(data)
        out = self.runs_dir / f"{run_id}.html"
        out.write_text(html, encoding="utf-8")
        return out

    def generate_index(self, limit: int = 50) -> Path:
        runs: List[dict] = []
        for jf in sorted(self.runs_dir.glob("*.json")):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                runs.append(data)
            except Exception:
                continue
        runs = sorted(runs, key=lambda x: x.get("started_at", 0), reverse=True)[:limit]
        html = self._render_index(runs)
        out = self.runs_dir / "index.html"
        out.write_text(html, encoding="utf-8")
        return out

    def _render_html(self, data: Any) -> str:
        status = "SUCCESS" if data.get("success") else "FAILED"
        return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Run {data.get('id')}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    .status-success {{ color: #0a0; }}
    .status-failed {{ color: #a00; }}
    pre {{ background: #f6f6f6; padding: 1rem; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>Run {data.get('id')}</h1>
  <p>Kind: {data.get('kind')}</p>
  <p>Manifest: {data.get('manifest')}</p>
  <p>Status: <strong class="status-{'success' if data.get('success') else 'failed'}">{status}</strong></p>
  <h2>Inputs</h2>
  <pre>{json.dumps(data.get('inputs'), indent=2)}</pre>
  <h2>Flags</h2>
  <pre>{json.dumps(data.get('flags'), indent=2)}</pre>
  <h2>Result Summary</h2>
  <pre>{json.dumps(data.get('result_summary'), indent=2)}</pre>
  <h2>Error</h2>
  <pre>{json.dumps(data.get('error'), indent=2)}</pre>
  <p>Started: {data.get('started_at')}</p>
  <p>Ended: {data.get('ended_at')}</p>
</body>
</html>"""

    def _render_index(self, runs: List[dict]) -> str:
        rows = "\n".join(
            f"<tr><td><a href='{r.get('id')}.html'>{r.get('id')}</a></td>"
            f"<td>{r.get('kind')}</td>"
            f"<td>{r.get('manifest')}</td>"
            f"<td>{'SUCCESS' if r.get('success') else 'FAILED'}</td>"
            f"<td>{r.get('started_at')}</td>"
            f"<td>{r.get('ended_at')}</td></tr>"
            for r in runs
        )
        return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Runs Index</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
  </style>
</head>
<body>
  <h1>Recent Runs</h1>
  <table>
    <thead><tr><th>ID</th><th>Kind</th><th>Manifest</th><th>Status</th><th>Started</th><th>Ended</th></tr></thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>"""