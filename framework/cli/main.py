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
from framework.core.sessions.store import SessionStore
from framework.core.sessions.docker_runtime import docker_available, run_container, stop_container

app = typer.Typer(help="Lab Security Framework (MVP scaffold) - Lab-only by default.")

modules_app = typer.Typer(help="Module management commands")
sessions_app = typer.Typer(help="Session commands")
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
sessions_store = SessionStore(RUNS_DIR / "sessions.json")

EULA_FILE = Path(".eula_accepted")
EULA_TEXT_PATH = Path("docs") / "EULA.md"


@app.callback()
def main(
    ctx: typer.Context,
    lab: bool = typer.Option(True, "--lab/--no-lab", help="Restrict to lab-only defaults"),
    agree: bool = typer.Option(False, "--agree", help="Agree to the ethical use EULA"),
):
    ctx.obj = {"lab": lab}
    if lab:
        print("[bold yellow]Lab mode is ON[/bold yellow] - public targets are blocked by default.")

    if agree:
        EULA_FILE.write_text("agreed", encoding="utf-8")

    # EULA gating
    if not EULA_FILE.exists():
        print("[bold red]Ethical Use Agreement not accepted[/bold red].")
        if EULA_TEXT_PATH.exists():
            print(f"Please read {EULA_TEXT_PATH} and rerun with --agree or run 'framework init --agree'.")
        else:
            print("Please rerun with --agree to accept the ethical use terms.")
        raise typer.Exit(code=1)


@app.command("init")
def init(agree: bool = typer.Option(False, "--agree", help="Agree to the ethical use EULA")):
    if agree:
        EULA_FILE.write_text("agreed", encoding="utf-8")
        print("EULA accepted.")
    else:
        if EULA_TEXT_PATH.exists():
            print(f"Read EULA at {EULA_TEXT_PATH}. Rerun with --agree to accept.")
        else:
            print("No EULA file found. Rerun with --agree to accept default ethical use terms.")


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


@modules_app.command("init")
def modules_init(
    module_id: str = typer.Argument(..., help="e.g., custom.probe.demo"),
    name: str = typer.Option(None, "--name", help="Human-friendly name"),
    type_: str = typer.Option("probe", "--type", help="probe|post|auxiliary"),
    out_dir: Path = typer.Option(DEFAULT_MODULES_DIR, "--out", help="Base modules directory"),
):
    parts = module_id.split(".")
    folder = out_dir / Path("/".join(parts))
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": module_id,
        "name": name or module_id,
        "version": "0.1.0",
        "type": type_,
        "platforms": ["linux", "windows", "macos"],
        "safety_level": "lab",
        "entry": "module:MyModule",
        "inputs": [],
        "outputs": [],
    }
    (folder / "module.yaml").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (folder / "module.py").write_text(
        "from typing import Dict, Any\nfrom framework.core.modules.base import Module\n\n"
        "class MyModule(Module):\n"
        "    metadata = {\"id\": \"" + module_id + "\", \"name\": \"" + (name or module_id) + "\", \"version\": \"0.1.0\", \"type\": \"" + type_ + "\", \"safety_level\": \"lab\"}\n"
        "    def __init__(self):\n        self.config: Dict[str, Any] = {}\n        self.env: Dict[str, Any] = {}\n"
        "    def validate(self, config: Dict[str, Any]) -> None:\n        self.config = config\n"
        "    def prepare(self, env: Dict[str, Any]) -> None:\n        self.env = env\n"
        "    def execute(self, session=None) -> Dict[str, Any]:\n        return {\"ok\": True}\n",
        encoding="utf-8",
    )
    print(f"Scaffolded module at {folder}")


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


@sessions_app.command("create")
def sessions_create(
    type_: str = typer.Option("local", "--type", help="local|docker"),
    image: Optional[str] = typer.Option(None, "--image", help="Docker image if type=docker"),
):
    meta = {}
    if type_ == "docker":
        if not docker_available():
            print("Docker is not available on this system.")
            raise typer.Exit(code=1)
        img = image or "alpine:latest"
        info = run_container(img, command="sleep 3600", detach=True)
        meta.update(info)
    sess = sessions_store.create(type_, meta)
    print(f"Session created: {sess['id']} ({sess['type']})")


@sessions_app.command("list")
def sessions_list():
    table = Table(title="Sessions")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("State")
    table.add_column("Meta")
    for s in sessions_store.list():
        table.add_row(s["id"], s["type"], s["state"], json.dumps(s.get("meta", {})))
    print(table)


@sessions_app.command("close")
def sessions_close(
    session_id: str = typer.Argument(...)
):
    # attempt to stop docker if associated
    sessions = sessions_store.list()
    for s in sessions:
        if s["id"] == session_id and s["state"] == "active":
            meta = s.get("meta", {}) or {}
            cid = meta.get("container_id")
            if cid:
                try:
                    stop_container(cid)
                except Exception:
                    pass
            break
    ok = sessions_store.close(session_id)
    if not ok:
        print(f"Session not found or not active: {session_id}")
        raise typer.Exit(code=1)
    print(f"Session closed: {session_id}")


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


@report_app.command("index")
def report_index():
    path = reporter.generate_index()
    print(f"Index: {path}")


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