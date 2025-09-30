import json
from pathlib import Path
from typing import Dict, Any

import yaml

from framework.core.modules.loader import ModuleLoader
from framework.core.metrics.collector import MetricsCollector
from framework.core.safety.guardrails import SafetyGuard


class ResourceRunner:
    def __init__(self, loader: ModuleLoader, metrics: MetricsCollector, guard: SafetyGuard, unsafe: bool = False):
        self.loader = loader
        self.metrics = metrics
        self.guard = guard
        self.unsafe = unsafe

    def run(self, path: Path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        steps = spec.get("steps", [])
        run_id = self.metrics.start_run(
            "resource",
            manifest_id=str(path),
            inputs={"vars": spec.get("vars", {})},
            flags={"unsafe": self.unsafe},
        )
        ctx: Dict[str, Any] = {"vars": spec.get("vars", {})}
        try:
            for step in steps:
                if "run" in step:
                    run_spec = step["run"]
                    mod_id = run_spec["module"]
                    with_inputs = self._render(run_spec.get("with", {}), ctx)
                    manifest = self.loader.get_manifest_by_id(mod_id)
                    if not manifest:
                        raise ValueError(f"Module not found: {mod_id}")
                    self.guard.validate_inputs(manifest, with_inputs, unsafe=self.unsafe)
                    module = self.loader.load_module(manifest)
                    module.validate(with_inputs)
                    module.prepare({"emulate": True})
                    result = module.execute(session=None)
                    result = module.postprocess(result)
                    alias = step.get("as", mod_id)
                    ctx[alias] = result
                elif "report" in step:
                    # no-op in MVP, report generated via CLI report show
                    pass
                else:
                    raise ValueError(f"Unknown step: {step}")
            self.metrics.end_run(run_id, success=True, result_summary=self._shorten(ctx))
            return run_id
        except Exception as e:
            self.metrics.end_run(run_id, success=False, error=str(e))
            raise

    def _render(self, data, ctx):
        if isinstance(data, str):
            return self._render_str(data, ctx)
        if isinstance(data, list):
            return [self._render(x, ctx) for x in data]
        if isinstance(data, dict):
            return {k: self._render(v, ctx) for k, v in data.items()}
        return data

    def _render_str(self, s: str, ctx):
        # very small interpolation of ${vars.name}
        if s.startswith("${") and s.endswith("}"):
            path = s[2 + 1 : -1].split(".")  # remove ${ and }
            cur = ctx
            for p in path:
                cur = cur[p]
            return cur
        return s

    def _shorten(self, obj, limit=2000):
        s = json.dumps(obj, default=str)
        if len(s) <= limit:
            return obj
        return {"_truncated": True, "preview": s[:limit] + "..."}