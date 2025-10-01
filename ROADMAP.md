Roadmap: v2.0 (Planned)
=======================

This document outlines high-impact features targeted for v2.0. The scope is CLI-only; no external API/server is planned.

1) Resource DSL Enhancements
- Operators: gt, lt, regex, exists, any/all
- Execution controls: continue_on_error, retry with backoff, per-step timeout
- Parallel foreach with concurrency limit
- Include/import for YAML (compose resources), external vars files, basic secrets support

2) Reporting and Analytics
- Templated HTML reports with module-type specific summaries
- Aggregate dashboard (success rate, durations, module usage)
- Multi-run comparisons and trends
- Export formats: JSON/CSV with stable schema; optional ELK/Grafana-friendly outputs

3) Sessions and Lab Profiles
- Docker lifecycle: logs, exec, file copy
- Network isolation presets (bridged networks, subnets), simple target linking
- Prebuilt vulnerable lab profiles (lab-only)
- Session-aware module execution and selection

4) Governance and Policy
- Policy file (policy.yaml): allowed modules, parameters, target guardrails
- Unsafe override justification (required note; logged in audit)
- Trust model bricks:
  - Module signing (optional), hash pinning, trusted registries
  - Safety levels enforced by policy

5) Module Ecosystem
- Safe auxiliary modules: HTTP probe, DNS/WHOIS, banner grab, JSON/CSV transforms
- Nmap runner (lab-only) + richer parse/normalize
- Module templates and generator presets per type
- Optional module registry (Git-based index or simple registry.json)

6) Developer Experience and Testing
- Typed config schemas (pydantic) with auto-validate
- Shell completions, richer help/usage examples
- Contract tests for modules and end-to-end resource scenarios
- Debug mode: step-by-step, context inspect, interpolation trace

7) Performance and Scale
- Parallel execution engine with rate limiting
- Caching layer for probe results (TTL)
- Streaming outputs for large results; summarized reports

8) DevOps and Distribution
- Release drafter and automated CHANGELOG for GitHub Releases
- PyPI trusted publishing via OIDC (secrets-free)
- Optional Homebrew formula and prebuilt binaries via PyInstaller (exploratory)

Notes
- Safety remains lab-first. No operational exploits/payloads will ship by default.
- Features will respect ethical use and policy configuration.