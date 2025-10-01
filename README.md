Lab Security Framework v1.0
===========================

[![CI](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml)
[![Publish](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/lab-sec-framework.svg)](https://pypi.org/project/lab-sec-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A safe, modular, lab-first security testing framework scaffold that focuses on
developer experience, automation, and governance. Ships with non-operational
example modules and strong guardrails. CLI-only. No API is exposed.

Quick start
- Install: pip install -e .
- Accept EULA: framework init --agree
- Version: framework --version
- List modules: framework modules list
- Run a module:
  framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Run a resource:
  framework resource run resources/examples/quick_probe.yaml
- Show last report:
  framework report show --last
- Generate runs index:
  framework report index
- Manage sessions:
  framework sessions create --type local
  framework sessions list
  framework sessions close <id>
  framework sessions create --type docker --image alpine:latest   # requires Docker
- Scaffold a new module:
  framework modules init custom.probe.demo --name "Demo Probe"

Özellikler (TR)
- Mevcut ve v2.0 planı için ayrıntılar: docs/features-tr.md

Görseller (Screenshots & Diagrams)
- Aşağıdaki Mermaid diyagramları GitHub üzerinde otomatik render edilir. PNG/JPG ekran görüntülerini `docs/media/images/` içine koyup README’de referanslayın (örnekler aşağıda).
- Ayrıntılar ve yönergeler: docs/media/README.md

```mermaid
%% Architecture (inline)
graph TD
  A[CLI (Typer)] --> B[Module Loader]
  A --> C[Resource Runner (DSL)]
  A --> D[Sessions (Local/Docker)]
  A --> E[Report Generator]
  A --> F[Metrics (JSON + SQLite)]
  B --> G[Modules (manifests + code)]
  G --> H[Safety Guardrails]
  C --> G
  C --> F
  E --> I[.runs/ HTML]
  F --> J[.runs/metrics.db]
  D --> K[Docker Runtime]
```

Screenshots (add your images under docs/media/images/)
- ![CLI Modules List](docs/media/images/cli-modules-list.png)
- ![Resource Run](docs/media/images/resource-run.png)
- ![Report Index](docs/media/images/report-index.png)

Publishing (GitHub & PyPI)
- GitHub Release:
  1) Bump version in pyproject.toml and CHANGELOG.md
  2) Create a tag (e.g., v1.0.0) and push
  3) Publish a GitHub Release from the tag
- PyPI Publish:
  - Configure repository secrets:
    - PYPI_API_TOKEN: PyPI token with publish rights
  - On publishing a GitHub Release, the workflow .github/workflows/publish.yml builds and uploads to PyPI

Roadmap: v2.0 (Coming)
- Resource DSL: regex/exists, gt/lt, any/all; retry, timeout, continue_on_error; parallel foreach
- Reporting: templated module summaries, aggregate dashboard, multi-run trends, JSON/CSV exports
- Sessions/Lab: Docker logs/exec/copy, network isolation presets, lab profiles, session-aware modules
- Governance: policy.yaml (allowed modules/params), unsafe justification logs, trust model (signing/pinning)
- Modules: HTTP/DNS/WHOIS probes, banner grab, JSON/CSV transforms, Nmap runner + richer parse
- DX/Test: typed config (pydantic), completions, contract tests, debug/trace mode
- Performance: parallel engine, caching, streaming large results
- DevOps: release-drafter, PyPI OIDC trusted publishing, optional Homebrew/binaries

See full roadmap: ROADMAP.md

Safety
- Lab mode is ON by default (blocks public IPs). Use --unsafe to override in a lab environment only.
- Example modules run in emulate mode by default.

License
- MIT License. See LICENSE file.

Docs
- docs/getting-started.md
- docs/module-dev-guide.md
- docs/architecture.md
- docs/EULA.md (EN/TR/RU)

Changelog
- See CHANGELOG.md for release notes.