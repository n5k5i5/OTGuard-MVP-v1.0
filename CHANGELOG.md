# Changelog

All notable changes to the OTGuard framework are documented in this file.

## [v2.0.0.dev1] - 2026-11-02 (Lead Developer: n5k5i5)

### Added
- **Rebranding & Identity:** Rebranded project to **OTGuard** (Operational Technology & ICS/SCADA Security Testing Framework).
- **New CLI Command:** Added `otguard` CLI entry point alongside legacy `framework`.
- **OT Protocol Modules:**
  - `ot.probe.modbus`: Modbus TCP (Port 502) Slave ID detection, Device Identification and holding register reader.
  - `ot.probe.s7comm`: Siemens S7comm / COTP (Port 102) ISO-on-TCP PLC fingerprinting.
  - `ot.probe.bacnet`: BACnet/IP (UDP 47808) Building Automation Who-Is device discovery.
  - `net.probe.http_banner`: Industrial Web & SCADA HMI banner grabber with vendor fingerprinting.
  - `ot.audit.weak_creds`: SCADA/HMI default vendor credential security auditor.
  - `util.transform.export`: Assessment findings exporter to JSON and CSV formats.
- **Resource DSL v2.0 Operators:**
  - Added numeric operators (`gt`, `lt`, `gte`, `lte`).
  - Added regular expression matching (`regex`) and field existence checks (`exists`).
  - Added logical connectors (`all`/`and`, `any`/`or`, `not`).
- **Comprehensive Scenario:** Added `resources/examples/ot_security_assessment.yaml`.
- **Unit Tests:** Added `tests/unit/test_ot_modules.py` and extended runner tests.
- **Skill Docs:** Added comprehensive `SKILL.md` and `.agents/skills/otguard/SKILL.md`.

---

## [v1.0.0] - 2025-09-30
- First stable MVP release. CLI-only; no API exposed.
- EULA gate for ethical use (EN/TR/RU).
- Module SDK, loader, and initial example modules (portscan, sysinfo, nmap import).
- Resource scripts with variables, loops (foreach), and simple conditionals (when).
- Sessions management stub with local and Docker-backed runtimes.
- Metrics and HTML reports with an index page.