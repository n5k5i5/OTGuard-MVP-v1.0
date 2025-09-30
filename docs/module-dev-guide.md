# Module Development Guide

This framework uses a simple manifest + Python class pattern.

## Manifest (module.yaml)
```yaml
id: examples.probe.portscan
name: Port Scanner (Example)
version: 0.1.0
type: probe
platforms: [linux, windows, macos]
safety_level: lab
entry: module:PortScanModule
inputs:
  - name: targets
    type: list[str]
    required: true
  - name: ports
    type: list[int]
    default: [22, 80, 443]
```

## Python module
```python
from framework.core.modules.base import Module

class MyModule(Module):
    metadata = {...}
    def validate(self, config): ...
    def prepare(self, env): ...
    def execute(self, session): ...
    def postprocess(self, result): return result
    def teardown(self): pass
```

## Loading and testing
- Place your module folder under `modules/` with a `module.yaml` and the Python file referenced by `entry`.
- List modules:
  ```
  framework modules list
  ```
- Run a module:
  ```
  framework run your.module.id --with key=value
  ```