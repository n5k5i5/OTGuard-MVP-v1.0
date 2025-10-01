# Features (EN)

This project is a safe, lab-first security testing scaffold (CLI-only). Below are current capabilities and the v2.0 roadmap.

## Current (v1.0)

- Modular architecture and module SDK
  - Develop modules with a manifest + Python class
  - Example modules (lab-safe): Port Scan, System Info, Nmap XML import
- Automation (Resource DSL)
  - YAML steps, variables, conditionals (`when`), loops (`foreach`)
  - Interpolation and dynamic aliases
- Reporting and metrics
  - Per-run JSON/HTML; runs index (.runs/index.html)
  - SQLite metrics database (.runs/metrics.db)
  - CLI activity logs in JSONL (.runs/app.log)
- Sessions (stubs)
  - Local and Docker-backed sessions
- Governance & safety
  - EULA (EN/TR/RU) acceptance gate
  - Safety Guardrails: lab mode, public IP block
  - Organization approval gate (OrgGate)
  - Optional second-factor for report generation (ReportGate)
- Packaging & distribution
  - PyPI/GitHub workflows; bundled example modules
- Documentation
  - Getting started, module developer guide, architecture, policy (OrgGate)

## Planned (v2.0 roadmap)

- ✅ Network Discovery: OT-aware identification
- ✅ Vulnerability Analysis: CVSS-based risk
- ✅ Reporting: multi-format (HTML/PDF/CSV/JSON)
- ✅ Database: SQLite persisted results with queries
- ✅ CLI & GUI: dual interfaces
- ✅ Logging: comprehensive, configurable logs
- ✅ Localized UI: Turkish, Russian support

Note
- Some roadmap items are not yet implemented. Track progress in ROADMAP.md and CHANGELOG.md.