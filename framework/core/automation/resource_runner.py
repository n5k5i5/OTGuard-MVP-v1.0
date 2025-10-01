import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

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
                # conditional execution
                when = step.get("when")
                if when is not None and not self._eval_when(when, ctx):
                    continue

                if "set" in step:
                    name = step["set"].get("name")
                    value = self._render(step["set"].get("value"), ctx)
                    if not name:
                        raise ValueError("set step requires 'name'")
                    ctx.setdefault("vars", {})[name] = value
                    continue

                if "foreach" in step:
                    loop = step["foreach"]
                    items = self._render(loop.get("list", []), ctx) or []
                    var_name = loop.get("as", "item")
                    body: List[dict] = loop.get("do", [])
                    for it in items:
                        ctx[var_name] = it
                        for b in body:
                            # nested when support
                            if "when" in b and not self._eval_when(b["when"], ctx):
                                continue
                            self._execute_step(b, ctx)
                    # cleanup temp var
                    if var_name in ctx:
                        ctx.pop(var_name)
                    continue

                # normal steps
                self._execute_step(step, ctx)

            self.metrics.end_run(run_id, success=True, result_summary=self._shorten(ctx))
            return run_id
        except Exception as e:
            self.metrics.end_run(run_id, success=False, error=str(e))
            raise

    def _execute_step(self, step: dict, ctx: Dict[str, Any]) -> None:
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
            alias_tpl = step.get("as", mod_id)
            alias = self._render(alias_tpl, ctx) if isinstance(alias_tpl, str) else alias_tpl
            ctx[str(alias)] = result
            return
        if "report" in step:
            # still a no-op in runner; reports are generated via CLI
            return
        raise ValueError(f"Unknown step: {step}")

    def _render(self, data, ctx):
        """
        Recursively render a nested data structure by interpolating any strings using the provided context.
        
        Strings are processed through the instance's interpolation logic; lists and dictionaries are traversed and rebuilt with their elements/values rendered recursively. Non-collection, non-string values are returned unchanged.
        
        Parameters:
            data: The value to render — may be a string, list, dict, or any other object.
            ctx: The rendering context used for interpolation (variable lookup and resolution).
        
        Returns:
            The same structure as `data` with all string values replaced by their interpolated results.
        """
        if isinstance(data, str):
            return self._interpolate(data, ctx)
        if isinstance(data, list):
            return [self._render(x, ctx) for x in data]
        if isinstance(data, dict):
            return {k: self._render(v, ctx) for k, v in data.items()}
        return data

    def _interpolate(self, s: str, ctx):
        # If the whole string is a single token, resolve it (support nested tokens inside)
        """
        Interpolate `${...}` tokens in a string using the provided context and return the resolved value.
        
        Parameters:
            s (str): Input string containing zero or more `${...}` tokens. If the entire string is a single token, the function will resolve and return the referenced value (which may be a non-string).
            ctx: Context used for resolving paths referenced by tokens.
        
        Returns:
            The resolved value for a single-token string (which can be any type), or a string with all `${...}` tokens replaced by their resolved textual representations.
        """
        if s.startswith("${") and s.endswith("}"):
            inner = s[2:-1]
            inner_resolved = self._interpolate(inner, ctx) if isinstance(inner, str) else inner
            if isinstance(inner_resolved, str):
                return self._resolve_path(inner_resolved, ctx)
            return inner_resolved

        if "${" not in s:
            return s

        # Replace non-nested ${...} tokens inside the string
        out = ""
        i = 0
        while i < len(s):
            start = s.find("${", i)
            if start == -1:
                out += s[i:]
                break
            out += s[i:start]
            end = s.find("}", start + 2)
            if end == -1:
                out += s[start:]
                break
            token = s[start + 2 : end]
            resolved = self._interpolate(token, ctx) if isinstance(token, str) else token
            if isinstance(resolved, str):
                value = self._resolve_path(resolved, ctx)
            else:
                value = resolved
            out += str(value)
            i = end + 1
        return out

    def _resolve_path(self, path: str, ctx):
        """
        Resolve a dot-separated path against the provided context and return the referenced value.
        
        Parameters:
            path (str): Dot-separated sequence of keys (e.g., "vars.user.name") identifying the value to retrieve.
            ctx: Mapping (typically the current execution context) to traverse using the keys in `path`.
        
        Returns:
            The value found at the specified path within `ctx`.
        """
        cur = ctx
        for p in path.split("."):
            cur = cur[p]
        return cur

    def _eval_when(self, expr, ctx) -> bool:
        # expr can be a truthy path string like "${alias.key}"
        # or a dict with simple operators: equals, contains
        if isinstance(expr, str):
            val = self._render(expr, ctx)
            return bool(val)
        if isinstance(expr, dict):
            if "equals" in expr:
                left, right = expr["equals"]
                left_v = self._render(left, ctx)
                right_v = self._render(right, ctx)
                return left_v == right_v
            if "contains" in expr:
                container, item = expr["contains"]
                cont_v = self._render(container, ctx)
                item_v = self._render(item, ctx)
                try:
                    return item_v in cont_v
                except Exception:
                    return False
        return False

    def _shorten(self, obj, limit=2000):
        s = json.dumps(obj, default=str)
        if len(s) <= limit:
            return obj
        return {"_truncated": True, "preview": s[:limit] + "..."}