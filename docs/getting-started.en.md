# Getting Started (EN)

This framework is a safe, lab-first scaffold for modular security testing. CLI-only, strong guardrails, and organization approval (OrgGate).

## Prerequisites
- Python 3.9+ (recommended: 3.11)
- Optional: Docker (for docker sessions)
- Optional: virtualenv or pipx

## Install

### 1) From PyPI (recommended)
```bash
# Optional virtual env
python -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install
pip install lab-sec-framework

# Verify
framework --version
```

### 2) From source (dev)
```bash
git clone https://github.com/your-org/lab-sec-framework.git
cd lab-sec-framework
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
framework --version
```

### 3) pipx (isolated user install)
```bash
pipx install lab-sec-framework
framework --version
```

### Windows notes
- You may need to set PowerShell ExecutionPolicy:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- Use `py -m pip` and `py -m venv` if needed.

## First run (EULA and language)
```bash
framework init --agree --lang en
```
- Alternatively, pass `--agree --lang en` with any command:
  ```bash
  framework modules list --agree --lang en
  ```

## Organization approval (required)
Before using core commands, complete OrgGate.

1) Initialize:
```bash
framework org init --name "ACME" --domain acme.com --email secops@acme.com
```
- If SMTP is configured, an email with token is sent. Otherwise, the token is shown in the CLI.
- Optional webhook: set `ORG_WEBHOOK_URL` to receive a JSON payload.

2) Clickable link (optional):
```bash
# Serve internal verification endpoint
framework org serve --host 0.0.0.0 --port 8080
```
- Set `ORG_VERIFY_BASE_URL=http://<host>:8080/verify` to embed a link in emails.
- Link: `http://<host>:8080/verify?token=<TOKEN>`

3) Verify via CLI:
```bash
framework org verify --token <TOKEN>
```

4) Status and reset:
```bash
framework org status
framework org reset --confirm
```

### SMTP/Webhook (optional)
- SMTP_HOST, SMTP_PORT (default 587)
- SMTP_USER, SMTP_PASS
- SMTP_FROM (default SMTP_USER)
- SMTP_TLS (true/false; default true)
- ORG_VERIFY_BASE_URL (optional; adds clickable email link)
- ORG_WEBHOOK_URL (optional; JSON POST on init)

## Basic usage
```bash
# List modules
framework modules list

# Run example (emulated)
framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'

# Resource automation
framework resource run resources/examples/quick_probe.yaml

# Reports (optional second factor)
framework report gate-set
framework report show --last --report-token <TOKEN>
framework report index --report-token <TOKEN>

# Sessions (optional)
framework sessions create --type local
framework sessions list
framework sessions close <id>
# Docker session (starts sleeping container)
framework sessions create --type docker --image alpine:latest
```

## Resource DSL: loop + condition
```yaml
version: "1"
name: "Loop Probe"
vars:
  targets: ["127.0.0.1", "127.0.0.2"]
steps:
  - set: { name: ports, value: [22, 80] }
  - foreach:
      list: "${vars.targets}"
      as: t
      do:
        - run:
            module: examples.probe.portscan
            with:
              targets: "${t}"
              ports: "${vars.ports}"
          as: "scan_${t}"
        - when: { contains: ["${scan_${t}.open_ports.${t}}", 80] }
          run:
            module: examples.post.sysinfo
          as: "sys_${t}"
```

## Update / Uninstall
```bash
pip install -U lab-sec-framework
pip uninstall lab-sec-framework
deactivate    # close virtual env
```

## Troubleshooting
- "framework" not found: check virtual env and PATH.
- Docker session errors: verify `docker --version` and daemon.
- JSON params: ensure quoting for `--with` (e.g., ports='[22,80,443]').

## License
- MIT. See LICENSE.

## Safety
- Lab mode ON by default (public IPs are blocked).
- Use `--unsafe` only in isolated labs and with authorization.