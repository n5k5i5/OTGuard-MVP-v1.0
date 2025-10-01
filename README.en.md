Lab Security Framework v1.0 (English)
=====================================

[![CI](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml)
[![Publish](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/lab-sec-framework.svg)](https://pypi.org/project/lab-sec-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Languages: [English](README.en.md) | [Türkçe](README.tr.md) | [Русский](README.ru.md)

A safe, modular, lab-first security testing framework scaffold. CLI-only, no API. Strong guardrails, organization approval gate, optional two-factor for reports, and packaged example modules.

Quick start
- Accept EULA and set language:
  - framework init --agree --lang en
- Organization approval (required):
  - framework org init --name "ACME" --domain acme.com --email secops@acme.com
  - Get token from email (or CLI if SMTP not configured)
  - framework org verify --token <TOKEN>
- List modules: framework modules list
- Run example (emulated):
  - framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Reports (optional 2FA):
  - framework report gate-set
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>

Install
- PyPI (recommended)
  1) Optional venv:
     - python -m venv .venv && source .venv/bin/activate
     - Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1
  2) pip install lab-sec-framework
  3) framework --version
- From source (dev)
  - git clone https://github.com/your-org/lab-sec-framework.git
  - cd lab-sec-framework
  - python -m venv .venv && source .venv/bin/activate
  - pip install -e .
- pipx
  - pipx install lab-sec-framework

Organization approval (OrgGate)
- Required before running core commands (modules/run/resource/report/sessions).
- Steps:
  1) framework org init --name "ACME" --domain acme.com --email secops@acme.com
  2) Receive token by email (SMTP) or from CLI (if SMTP not set)
     - Optional clickable link:
       - Run local server: framework org serve --host 0.0.0.0 --port 8080
       - Set ORG_VERIFY_BASE_URL=http://<host>:8080/verify
  3) framework org verify --token <TOKEN>
- Status/Reset:
  - framework org status
  - framework org reset --confirm
- Optional Webhook:
  - ORG_WEBHOOK_URL: send JSON payload on init

Report two-factor (ReportGate) – optional
- Enable:
  - framework report gate-set
- Use:
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>
- Manage:
  - framework report gate-status
  - framework report gate-disable

Core commands
- framework modules list
- framework run <module> --with key=value
- framework resource run <path.yaml>
- framework report show --last | --run-id <id>
- framework report index
- framework sessions create --type local|docker [--image alpine:latest]
- framework sessions list | close <id>
- framework modules init custom.probe.demo --name "Demo Probe" --type probe

Docs
- Getting started: docs/getting-started.en.md
- Org approval: docs/policy/org-approval.en.md
- Architecture: docs/architecture.md
- EULA: docs/EULA.md (EN/TR/RU)
- Features: docs/features-en.md

Diagrams and screenshots
- See docs/media/README.md
- Inline architecture (Mermaid):

```mermaid
graph TD
  A[CLI (Typer)] --> B[Module Loader]
  A --> C[Resource Runner (DSL)]
  A --> D[Sessions (Local/Docker)]
  A --> E[Report Generator]
  A --> F[Metrics (JSON + SQLite)]
  A --> O[OrgGate / ReportGate]
  B --> G[Modules (manifests + code)]
  G --> H[Safety Guardrails]
  C --> G
  C --> F
  E --> I[.runs/ HTML]
  F --> J[.runs/metrics.db]
  D --> K[Docker Runtime]
```

Safety
- Lab mode ON by default (blocks public IPs). Use --unsafe only in isolated labs and with authorization.
- Example modules run in emulate mode.

License
- MIT. See LICENSE.

Roadmap
- See ROADMAP.md and docs/features-en.md.