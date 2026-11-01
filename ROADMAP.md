# OTGuard Roadmap: v2.0

> **Lead Architect:** `n5k5i5`  
> High-impact features targeted for OTGuard v2.0. Scope is CLI-only and Lab-safe.

## 1) Resource DSL Enhancements
- [x] **v2.0-dev1 Operators:** `gt`, `lt`, `gte`, `lte`, `regex`, `exists`, `all`/`and`, `any`/`or`, `not`
- [ ] Execution controls: `continue_on_error`, retry with backoff, per-step timeout
- [ ] Parallel foreach with concurrency limit
- [ ] Include/import for YAML (compose resources), external vars files, secrets support

## 2) Module Ecosystem (OT / ICS Focus)
- [x] **v2.0-dev1:** Modbus TCP probe & diagnostic (`ot.probe.modbus`)
- [x] **v2.0-dev1:** Siemens S7comm / COTP probe (`ot.probe.s7comm`)
- [x] **v2.0-dev1:** BACnet/IP building automation probe (`ot.probe.bacnet`)
- [x] **v2.0-dev1:** Industrial HMI & Web banner grabber (`net.probe.http_banner`)
- [x] **v2.0-dev1:** Default OT weak credential auditor (`ot.audit.weak_creds`)
- [x] **v2.0-dev1:** Assessment export to JSON/CSV (`util.transform.export`)
- [ ] EtherNet/IP & CIP probe (`ot.probe.ethernetip`)
- [ ] OPC UA Endpoint & security policy explorer (`ot.probe.opcua`)

## 3) Reporting and Analytics
- [x] JSON/CSV exporter module
- [ ] Templated interactive HTML reports with OT asset classification
- [ ] Aggregate multi-run trends & metrics dashboard

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