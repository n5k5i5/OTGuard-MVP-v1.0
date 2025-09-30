from pathlib import Path
import yaml

from framework.core.modules.loader import ModuleLoader
from framework.core.automation.resource_runner import ResourceRunner
from framework.core.metrics.collector import MetricsCollector
from framework.core.safety.guardrails import SafetyGuard


def test_resource_runner_conditions_and_loops(tmp_path: Path):
    # Build a temporary resource spec using loops, set, and when conditions
    spec = {
        "version": "1",
        "name": "Loop Probe",
        "vars": {"targets": ["127.0.0.1", "127.0.0.2"]},
        "steps": [
            {"set": {"name": "ports", "value": [22, 80]}},
            {
                "foreach": {
                    "list": "${vars.targets}",
                    "as": "t",
                    "do": [
                        {
                            "run": {
                                "module": "examples.probe.portscan",
                                "with": {"targets": "${t}", "ports": "${vars.ports}"},
                            },
                            "as": "scan_${t}",
                        },
                        {
                            "when": {"contains": ["${scan_${t}.open_ports.${t}}", 80]},
                            "run": {"module": "examples.post.sysinfo"},
                            "as": "sys_${t}",
                        },
                    ],
                }
            },
        ],
    }
    res_file = tmp_path / "resource.yaml"
    res_file.write_text(yaml.safe_dump(spec), encoding="utf-8")

    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    loader = ModuleLoader([Path("modules")])
    metrics = MetricsCollector(runs_dir)
    guard = SafetyGuard()
    runner = ResourceRunner(loader=loader, metrics=metrics, guard=guard, unsafe=False)

    rid = runner.run(res_file)
    assert rid == metrics.latest_run_id()