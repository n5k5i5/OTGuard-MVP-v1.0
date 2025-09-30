# Architecture Overview

## Components
- CLI (Typer): `framework/cli/main.py`
- Module SDK: `framework/core/modules/base.py`
- Manifest + Loader: `framework/core/modules/manifest.py`, `framework/core/modules/loader.py`
- Resource Runner: `framework/core/automation/resource_runner.py`
- Sessions (stub): `framework/core/sessions/*`
- Metrics + Reports: `framework/core/metrics/collector.py`, `framework/core/report/generator.py`
- Safety Guardrails: `framework/core/safety/guardrails.py`

## Flow
1. User runs CLI command.
2. Loader discovers manifest(s) under `modules/`.
3. Guardrails validate inputs (e.g., targets must be private by default).
4. Module is imported dynamically and executed in emulate mode by default.
5. Metrics are persisted to `.runs/{id}.json`.
6. Report generator converts a run into a basic HTML report or an index.

## Resource DSL (MVP)
- Interpolation: `${path.to.value}` referencing previous step aliases or `vars.*`.
- Steps:
  - `run`: execute a module
  - `report`: placeholder for report hints
  - `set`: set a variable into `vars`
  - `foreach`: loop over a list with `as` and a `do` body
- Conditionals:
  - `when`: supports simple forms:
    - String path truthiness: `when: \"${alias.key}\"`
    - Operators:
      - `equals: [left, right]`
      - `contains: [container, item]`
  - All operands support interpolation.

## Safety
- Lab-only defaults.
- Public IP targets blocked unless `--unsafe` is used.
- Example modules are non-operational by default (emulate mode).