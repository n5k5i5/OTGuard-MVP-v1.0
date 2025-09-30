import json
from pathlib import Path
from typing import Optional, List

import typer
from rich import print
from rich.table import Table

from framework.core.modules.loader import ModuleLoader
from framework.core.automation.resource_runner import ResourceRunner
from framework.core.metrics.collector import MetricsCollector
from framework.core.report.generator import ReportGenerator
from framework.core.safety.guardrails import SafetyGuard

app = typer.Typer(help="Lab Security Framework (MVP scaffold) - Lab-only by default.")

modules_app = typer.Typer(help="Module management commands")
sessions_app = typer.Typer(help="Session commands (stub)")
resource_app = typer.Typer(help="Resource script runner")
report_app = typer.Typer(help="Reporting commands")

app.add_typer(modules_app, name="modules")
app.add_typer(sessions_app, name="sessions")
app.add_typer(resource_app, name="resource")
app.add_typer(report_app, name="report")

DEFAULT_MODULES_DIR = Path("modules")
RUNS_DIR = Path(".runs")
RUNS_DIR.mkdir(exist_ok=True)

metrics = MetricsCollector(RUNS_DIR)
reporter = ReportGenerator(RUNS_DIR)
guard = SafetyGuard()


@app.callback()
def main(
    ctx: typer.Context,
    lab: bool = typer.Option(True, "--lab/--no-lab", help="Restrict to lab-only defaults"),
):
    ctx.obj = {"lab": lab}
    if lab:
        print("[bold yellow]Lab mode is ON[/bold yellow] - public targets are blocked by default.")


@modules_app.command("list")
def modules_list(
    modules_dir: Path = typer.Option(DEFAULT_MODULES_DIR, exists=True, file_okay=False),
):
    loader = ModuleLoader([modules_dir])
    loaded = loader.discover()
    table = Table(title="Available Modules")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Version")
    table.add_column("Safety")
    for m in loaded:
        table.add_row(
            m["id"], m.get("name", ""), m.get("type", ""), str(m.get("version", "")), m.get("safety_level", "lab")
        )
    print(table)


@app.command("run")
def run_module(
    module_id: str = typer.Argument(..., help="Module ID from manifest"),
    with_kv: List[str] = typer.Option(None, "--with", help="key=value pairs for module inputs"),
    modules_dir: Path = typer.Option(DEFAULT_MODULES_DIR, exists=True, file_okay=False),
    emulate: bool = typer.Option(True, "--emulate/--no-emulate", help="Run module in emulation mode if supported"),
    unsafe: bool = typer.Option(False, "--unsafe", help="Bypass guardrails (logged)"),
):
    loader = ModuleLoader([modules_dir])
    manifest = loader.get_manifest_by_id(module_id)
    if not manifest:
        raise typer.BadParameter(f"Module '{module_id}' not found")

    inputs = _parse_kv_list(with_kv or [])
    guard.validate_inputs(manifest, inputs, unsafe=unsafe)

    run_id = metrics.start_run("single", manifest_id=module_id, inputs=inputs, flags={"emulate": emulate, "unsafe": unsafe})
    module = loader.load_module(manifest)
    try:
        module.validate(inputs)
        module.prepare({"emulate": emulate})
        result = module.execute(session=None)
        result = module.postprocess(result or {})
        metrics.end_run(run_id, success=True, result_summary=_shorten(result))
        print(json.dumps(result, indent=2))
    except Exception as e:
        metrics.end_run(run_id, success=False, error=str(e))
        raise
    finally:
        try:
            module.teardown()
        except Exception:
            pass


@resource_app.command("run")
def resource_run(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
    modules_dir: Path = typer.Option(DEFAULT_MODULES_DIR, exists=True, file_okay=False),
    unsafe: bool = typer.Option(False, "--unsafe", help="Bypass guardrails (logged)"),
):
    loader = ModuleLoader([modules_dir])
    runner = ResourceRunner(loader=loader, metrics=metrics, guard=guard, unsafe=unsafe)
    run_id = runner.run(path)
    print(f"Resource executed. Run ID: {run_id}")


@sessions_app.command("list")
def sessions_list():
    table = Table(title="Sessions (stub)")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("State")
    print(table)


@report_app.command("show")
def report_show(
    last: bool = typer.Option(True, "--last/--no-last"),
    run_id: Optional[str] = typer.Option(None, help="Specific run id to show"),
):
    if last:
        rid = metrics.latest_run_id()
    else:
        rid = run_id
    if not rid:
        print("No runs found.")
        raise typer.Exit(code=1)
    report_path = reporter.generate_html(rid)
    print(f"Report: {report_path}")


def _parse_kv_list(items: List[str]) -> dict:
    out = {}
    for item in items:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --with item '{item}', expected key=value")
        k, v = item.split("=", 1)
        # try to parse JSON values, fallback to string
        try:
            out[k] = json.loads(v)
        except Exception:
            out[k] = v
    return out


def _shorten(obj, limit=2000):
    s = json.dumps(obj, default=str)
    if len(s) <= limit:
        return obj
    return {"_truncated": True, "preview": s[:limit] + "..."}