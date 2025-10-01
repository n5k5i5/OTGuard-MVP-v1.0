# Lab Security Framework v1.0

This repository is a safe, lab-first scaffold for a modular security testing framework.
It ships with non-operational example modules and strong guardrails.

## Prerequisites
- Python 3.9+
- Optional: virtualenv

## Install
```bash
pip install -e .
```

## First run
```bash
# Accept ethical use agreement (pick language: en|tr|ru)
framework init --agree --lang tr

# Check version
framework --version

# Explore modules
framework modules list

# Execute example module (emulated)
framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'

# Run resource script
framework resource run resources/examples/quick_probe.yaml

# Generate and open report for last run
framework report show --last

# Generate runs index
framework report index
```

## Resource scripts: loops and conditionals
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

## Sessions (optional)
```bash
# Requires Docker installed for docker sessions
framework sessions create --type local
framework sessions list
framework sessions close <id>

# Docker-backed (starts a container that sleeps)
framework sessions create --type docker --image alpine:latest
```

## License
- MIT License. See LICENSE file.

## Safety
- Lab mode is ON by default (public IPs are blocked).
- Use `--unsafe` only in an isolated lab and with proper authorization.