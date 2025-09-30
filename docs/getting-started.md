# Lab Security Framework (MVP Scaffold)

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
# Accept ethical use agreement
framework init --agree

# Explore modules
framework modules list

# Execute example module (emulated)
framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'

# Run resource script
framework resource run resources/examples/quick_probe.yaml

# Generate and open report for last run
framework report show --last
```

## Safety
- Lab mode is ON by default (public IPs are blocked).
- Use `--unsafe` only in an isolated lab and with proper authorization.