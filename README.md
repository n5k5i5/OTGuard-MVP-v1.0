Lab Security Framework v1.0
===========================

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

Publishing (GitHub & PyPI)
- GitHub Release:
  1) Bump version in pyproject.toml and CHANGELOG.md
  2) Create a tag (e.g., v1.0.0) and push
  3) Publish a GitHub Release from the tag
- PyPI Publish:
  - Configure repository secrets:
    - PYPI_API_TOKEN: PyPI token with publish rights
  - On publishing a GitHub Release, the workflow .github/workflows/publish.yml builds and uploads to PyPI

Safety
- Lab mode is ON by default (blocks public IPs). Use --unsafe to override in a lab environment only.
- Example modules run in emulate mode by default.

License
- MIT License. See LICENSE file.

Docs
- docs/getting-started.md
- docs/module-dev-guide.md
- docs/architecture.md
- docs/EULA.md

Changelog
- See CHANGELOG.md for release notes.