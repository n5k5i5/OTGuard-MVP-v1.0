# OTGuard (v2.0) - Getting Started Guide

> **Author & Architect:** `n5k5i5`  
> OTGuard is a lab-first, safe security testing and automation framework focused on Operational Technology (OT), SCADA, and Industrial Control Systems (ICS).

## Prerequisites
- Python 3.9+
- Optional: Docker (for isolated lab profiles)

## Installation
```bash
git clone https://github.com/n5k5i5/OTGuard.git
cd OTGuard
pip install -e .
```

## First Run
```bash
# Accept ethical use agreement (choose language: tr|en|ru)
otguard init --agree --lang tr

# Check version
otguard --version

# Explore installed OT & IT modules
otguard modules list

# Execute Modbus probe module (emulated by default)
otguard run ot.probe.modbus --with targets=127.0.0.1 --with port=502

# Run comprehensive OT assessment scenario
otguard resource run resources/examples/ot_security_assessment.yaml

# Generate and view report for the latest run
otguard report show --last

# Generate runs index
otguard report index
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