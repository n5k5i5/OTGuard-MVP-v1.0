Lab Security Framework (MVP Scaffold)
=====================================

A safe, modular, lab-first security testing framework scaffold that focuses on
developer experience, automation, and governance. Ships with non-operational
example modules and strong guardrails.

Quick start
- Install: pip install -e .
- Accept EULA: framework init --agree
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

Safety
- Lab mode is ON by default (blocks public IPs). Use --unsafe to override in a lab environment only.
- Example modules run in emulate mode by default.

Docs
- docs/getting-started.md
- docs/module-dev-guide.md
- docs/architecture.md
- docs/EULA.md