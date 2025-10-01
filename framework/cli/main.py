import json
from pathlib import Path
from typing import Optional, List
import importlib.metadata as importlib_metadata

import typer
from rich import print
from rich.table import Table

from framework.core.modules.loader import ModuleLoader
from framework.core.automation.resource_runner import ResourceRunner
from framework.core.metrics.collector import MetricsCollector
from framework.core.metrics.logger import AppLogger
from framework.core.report.generator import ReportGenerator
from framework.core.safety.guardrails import SafetyGuard
from framework.core.sessions.store import SessionStore
from framework.core.sessions.docker_runtime import docker_available, run_container, stop_container
from framework.core.policy.org_gate import OrgGate
from framework.core.policy.report_gate import ReportGate
from framework.core.policy.org_server import OrgHTTPServer
from framework.core.notify.emailer import Emailer
from framework.core.notify.webhook import WebhookNotifier

app = typer.Typer(help="Lab Security Framework (MVP scaffold) - Lab-only by default.")

modules_app = typer.Typer(help="Module management commands")
sessions_app = typer.Typer(help="Session commands")
resource_app = typer.Typer(help="Resource script runner")
report_app = typer.Typer(help="Reporting commands")
org_app = typer.Typer(help="Organization/company approval commands")

app.add_typer(modules_app, name="modules")
app.add_typer(sessions_app, name="sessions")
app.add_typer(resource_app, name="resource")
app.add_typer(report_app, name="report")
app.add_typer(org_app, name="org")

# Prefer local modules/ during development; fall back to bundled examples in package
PKG_DIR = Path(__file__).resolve().parent.parent
BUNDLED_MODULES_DIR = PKG_DIR / "bundled" / "modules"
DEFAULT_MODULES_DIR = Path("modules") if Path("modules").exists() else BUNDLED_MODULES_DIR
RUNS_DIR = Path(".runs")
RUNS_DIR.mkdir(exist_ok=True)

metrics = MetricsCollector(RUNS_DIR)
app_logger = AppLogger(RUNS_DIR / "app.log")
reporter = ReportGenerator(RUNS_DIR)
guard = SafetyGuard()
sessions_store = SessionStore(RUNS_DIR / "sessions.json")

# Org gate
emailer = Emailer()
webhook = WebhookNotifier()
org_gate = OrgGate(RUNS_DIR, emailer=emailer, webhook=webhook)
# Report gate
report_gate = ReportGate(RUNS_DIR)

EULA_FILE = Path(".eula_accepted")
EULA_TEXT_PATH = Path("docs") / "EULA.md"


def _version_callback(value: bool):
    if value:
        try:
            v = importlib_metadata.version("lab-sec-framework")
        except importlib_metadata.PackageNotFoundError:
            v = "1.0.0"
        print(v)
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    lab: bool = typer.Option(True, "--lab/--no-lab", help="Restrict to lab-only defaults"),
    agree: bool = typer.Option(False, "--agree", help="Agree to the ethical use EULA"),
    lang: str = typer.Option("en", "--lang", help="EULA language: en|tr|ru"),
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit", callback=_version_callback, is_eager=True),
):
    ctx.obj = {"lab": lab}
    if lab:
        print("[bold yellow]Lab mode is ON[/bold yellow] - public targets are blocked by default.")

    if agree:
        (RUNS_DIR / ".eula_lang").write_text(lang, encoding="utf-8")
        EULA_FILE.write_text("agreed", encoding="utf-8")

    # EULA gating
    if not EULA_FILE.exists():
        print("[bold red]Ethical Use Agreement not accepted[/bold red].")
        print(_eula_notice(lang))
        if EULA_TEXT_PATH.exists():
            print(f"Read full EULA: {EULA_TEXT_PATH}")
        print("Rerun with --agree or run 'framework init --agree' to accept.")
        raise typer.Exit(code=1)

    # Organization approval gating
    # Allow: no subcommand (help), 'init', 'org' group, 'about'
    allowed = {None, "init", "org", "about"}
    if not org_gate.is_verified():
        if ctx.invoked_subcommand not in allowed:
            print("[bold red]Organization approval required[/bold red].")
            print("Company information and explicit approval must be completed before use.")
            print("Steps:")
            print("  1) framework org init --name \"ACME\" --domain acme.com --email secops@acme.com")
            print("  2) Check company email for the verification token")
            print("  3) framework org verify --token <TOKEN>")
            raise typer.Exit(code=1)


@app.command("init")
def init(
    agree: bool = typer.Option(False, "--agree", help="Agree to the ethical use EULA"),
    lang: str = typer.Option("en", "--lang", help="EULA language: en|tr|ru"),
):
    app_logger.log("command", {"name": "init", "agree": agree, "lang": lang})
    if agree:
        (RUNS_DIR / ".eula_lang").write_text(lang, encoding="utf-8")
        EULA_FILE.write_text("agreed", encoding="utf-8")
        print(f"EULA accepted (lang={lang}).")
    else:
        if EULA_TEXT_PATH.exists():
            print(f"Read EULA at {EULA_TEXT_PATH}. Rerun with --agree to accept.")
        else:
            print("No EULA file found. Rerun with --agree to accept default ethical use terms.")


@modules_app.command("list")
def modules_list(
    modules_dir: Path = typer.Option(DEFAULT_MODULES_DIR, exists=True, file_okay=False),
):
    app_logger.log("command", {"name": "modules list", "modules_dir": str(modules_dir)})
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
    app_logger.log("command", {"name": "modules init", "module_id": module_id, "type": type_, "out_dir": str(out_dir)})
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
    app_logger.log("command", {"name": "run", "module_id": module_id, "emulate": emulate, "unsafe": unsafe})
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
    app_logger.log("command", {"name": "resource run", "path": str(path), "unsafe": unsafe})
    loader = ModuleLoader([modules_dir])
    runner = ResourceRunner(loader=loader, metrics=metrics, guard=guard, unsafe=unsafe)
    run_id = runner.run(path)
    print(f"Resource executed. Run ID: {run_id}")


@sessions_app.command("create")
def sessions_create(
    type_: str = typer.Option("local", "--type", help="local|docker"),
    image: Optional[str] = typer.Option(None, "--image", help="Docker image if type=docker"),
):
    app_logger.log("command", {"name": "sessions create", "type": type_, "image": image})
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
    app_logger.log("command", {"name": "sessions list"})
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
    app_logger.log("command", {"name": "sessions close", "session_id": session_id})
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
    report_token: Optional[str] = typer.Option(None, "--report-token", help="Second-factor token if enabled"),
):
    if last:
        rid = metrics.latest_run_id()
    else:
        rid = run_id
    if not rid:
        print("No runs found.")
        raise typer.Exit(code=1)
    if not report_gate.require(report_token):
        print("[bold red]Report generation requires a valid token[/bold red].")
        print("Generate or disable the guard:")
        print("  - framework report gate-set     # shows token")
        print("  - framework report gate-disable")
        print("  - framework report gate-status")
        raise typer.Exit(code=1)
    app_logger.log("command", {"name": "report show", "run_id": rid})
    report_path = reporter.generate_html(rid)
    print(f"Report: {report_path}")


@report_app.command("index")
def report_index(
    report_token: Optional[str] = typer.Option(None, "--report-token", help="Second-factor token if enabled"),
):
    if not report_gate.require(report_token):
        print("[bold red]Report index requires a valid token[/bold red].")
        print("See: framework report gate-set | gate-disable | gate-status")
        raise typer.Exit(code=1)
    app_logger.log("command", {"name": "report index"})
    path = reporter.generate_index()
    print(f"Index: {path}")


@report_app.command("gate-set")
def report_gate_set():
    app_logger.log("command", {"name": "report gate-set"})
    token = report_gate.set_token()
    print("Report gate enabled. Use this token when generating reports:")
    print(f"Token: {token}")
    print("Pass with: --report-token <TOKEN>")


@report_app.command("gate-disable")
def report_gate_disable():
    app_logger.log("command", {"name": "report gate-disable"})
    report_gate.disable()
    print("Report gate disabled.")


@report_app.command("gate-status")
def report_gate_status():
    app_logger.log("command", {"name": "report gate-status"})
    print("Enabled:" if report_gate.is_enabled() else "Disabled")


# --- Organization approval commands ---

@org_app.command("init")
def org_init(
    name: str = typer.Option(..., "--name", help="Organization name"),
    domain: str = typer.Option(..., "--domain", help="Primary domain (e.g., acme.com)"),
    email: str = typer.Option(..., "--email", help="Approver email (security/contact)"),
):
    app_logger.log("command", {"name": "org init", "org": name, "domain": domain, "email": email})
    token = org_gate.init_org(name=name, domain=domain, email=email)
    if emailer.is_configured():
        print("Organization initialized. Verification email sent.")
    else:
        print("Organization initialized. SMTP not configured; share this token with approver:")
        print(f"Token: {token}")
        print("Approver can authorize via: framework org verify --token <TOKEN>")

@org_app.command("status")
def org_status():
    app_logger.log("command", {"name": "org status"})
    st = org_gate.status()
    print(json.dumps(st, indent=2))

@org_app.command("verify")
def org_verify(token: str = typer.Option(..., "--token", help="Verification token")):
    app_logger.log("command", {"name": "org verify"})
    ok = org_gate.verify(token)
    if not ok:
        print("Verification failed. Check token and try again.")
        raise typer.Exit(code=1)
    print("Organization verified. You may now use the system.")

@org_app.command("reset")
def org_reset(confirm: bool = typer.Option(False, "--confirm", help="Confirm reset")):
    app_logger.log("command", {"name": "org reset"})
    if not confirm:
        print("Add --confirm to proceed. This will clear organization approval.")
        raise typer.Exit(code=1)
    org_gate.reset()
    print("Organization approval reset. Re-run org init to start again.")


@org_app.command("serve")
def org_serve(
    host: str = typer.Option("0.0.0.0", "--host", help="Bind host"),
    port: int = typer.Option(8080, "--port", help="Bind port"),
):
    app_logger.log("command", {"name": "org serve", "host": host, "port": port})
    print(f"Organization verification HTTP server listening on http://{host}:{port}/verify?token=...")
    print("Press Ctrl+C to stop.")
    server = OrgHTTPServer(host, port, verifier=org_gate.verify)
    try:
        server.serve()
    except KeyboardInterrupt:
        print("Server stopped.")


@app.command("about")
def about():
    app_logger.log("command", {"name": "about"})
    print("Özellikler (TR) - kısa özet:")
    print("- Modüler mimari ve modül SDK'sı")
    print("- Otomasyon (Resource DSL): değişkenler, koşullar, döngüler")
    print("- Raporlama: HTML/JSON ve çalışma indeksi")
    print("- Oturumlar: local ve Docker stub")
    print("- Güvenlik: EULA (EN/TR/RU), lab modunda guardrails")
    print("- Paketleme: PyPI/GitHub yayın")
    print("- Ayrıntılar için: docs/features-tr.md")


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


def _eula_notice(lang: str) -> str:
    lang = (lang or "en").lower()
    if lang.startswith("tr"):
        return (
            "Kullanım Sözleşmesi (Özet): Bu yazılım yalnızca izole lab ortamlarında, yasal ve yetkili "
            "güvenlik testleri için sağlanır. Kullanım tamamen kullanıcı sorumluluğundadır. "
            "Tüm ilgili kanunlara uyulmalıdır. Yazarlar/katkıcılar hukuki sonuç ve zararlardan sorumlu değildir."
        )
    if lang.startswith("ru"):
        return (
            "Краткое соглашение: ПО предназначено только для законного, этичного и санкционированного "
            "тестирования в изолированных лабораториях. Ответственность за использование несет пользователь. "
            "Соблюдайте все применимые законы. Авторы/участники не несут ответственности за последствия."
        )
    return (
        "EULA Summary: This software is for lawful, authorized testing in isolated labs only. "
        "You are solely responsible for use. Comply with applicable laws. "
        "Authors/contributors are not liable for misuse or consequences."
    )