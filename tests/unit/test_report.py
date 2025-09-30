import json
from pathlib import Path

from framework.core.metrics.collector import MetricsCollector
from framework.core.report.generator import ReportGenerator


def test_generate_index(tmp_path: Path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    metrics = MetricsCollector(runs_dir)
    rid1 = metrics.start_run("single", "mod1", {}, {})
    metrics.end_run(rid1, success=True, result_summary={})
    rid2 = metrics.start_run("single", "mod2", {}, {})
    metrics.end_run(rid2, success=False, error="x")
    reporter = ReportGenerator(runs_dir)
    reporter.generate_html(rid1)
    reporter.generate_html(rid2)
    idx = reporter.generate_index()
    assert idx.exists()
    content = idx.read_text(encoding="utf-8")
    assert rid1 in content and rid2 in content