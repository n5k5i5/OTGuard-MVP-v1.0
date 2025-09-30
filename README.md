Lab Security Framework (MVP Scaffold)
=====================================

A safe, modular, lab-first security testing framework scaffold that focuses on
developer experience, automation, and governance. Ships with non-operational
example modules and strong guardrails.

Quick start
- Install: pip install -e .
- List modules: framework modules list
- Run a module:
  framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Run a resource:
  framework resource run resources/examples/quick_probe.yaml
- Show last report:
  framework report show --last

Safety
- Lab mode is ON by default (blocks public IPs). Use --unsafe to override in a lab environment only.
- Example modules run in emulate mode by default.

Docs
- docs/getting-started.md
- docs/module-dev-guide.md
- docs/architecture.md