# Architecture Overview

## Components
- CLI (Typer): `framework/cli/main.py`
- Module SDK: `framework/core/modules/base.py`
- Manifest + Loader: `framework/core/modules/manifest.py`, `framework/core/modules/loader.py`
- Resource Runner: `framework/core/automation/resource_runner.py`
- Sessions (stub): `framework/core/sessions/*`
- Metrics + Reports: `framework/core/metrics/collector.py`, `framework/core/report/generator.py`
- Safety Guardrails: `framework/core/safety/guardrails.py`
- Governance:
  - Organization Approval (OrgGate): `framework/core/policy/org_gate.py`
  - Report Two-Factor (ReportGate): `framework/core/policy/report_gate.py`
  - (Optional) HTTP verify endpoint: `framework/core/policy/org_server.py`
- Notifications:
  - SMTP emailer: `framework/core/notify/emailer.py`
  - Webhook notifier: `framework/core/notify/webhook.py`
- Bundled Examples:
  - `framework/bundled/modules/examples` (fallback when local `modules/` not present)

## Flow
1. User runs CLI command.
2. EULA and OrgGate are enforced before core actions (allowed pre-verify: help/init/org/about).
3. Loader discovers manifest(s) under `modules/` or bundled examples.
4. Guardrails validate inputs (public targets blocked by default).
5. Module is imported dynamically and executed (examples emulate by default).
6. Metrics are persisted to `.runs/{id}.json` and summarized in SQLite `.runs/metrics.db`.
7. Report generator creates per-run HTML or an index; optional 2FA (ReportGate) can be required.

## Resource DSL (enhanced MVP)
- Interpolation:
  - Full-string and partial `${path.to.value}`, dynamic alias names (e.g., `scan_${t}`)
- Steps:
  - `run`: execute a module
  - `set`: write a value into `vars`
  - `foreach`: iterate a list with `as` and nested `do` steps
- Conditionals:
  - `when`: truthy path strings and operators:
    - `equals: [left, right]`
    - `contains: [container, item]`
  - All operands fully support interpolation.

## Observability
- Per-run JSON and `.runs/metrics.db` (SQLite) with a `runs` table.
- CLI JSONL logs at `.runs/app.log`.
- HTML index of runs at `.runs/index.html`.

## Safety
- Lab-only defaults.
- Public IP targets blocked unless `--unsafe` is used.
- Example modules are non-operational by default (emulate mode).
- OrgGate (mandatory) and ReportGate (optional) add governance and control layers.