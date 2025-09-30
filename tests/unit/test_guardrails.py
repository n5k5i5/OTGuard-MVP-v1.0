import pytest
from pathlib import Path

from framework.core.modules.loader import ModuleLoader
from framework.core.safety.guardrails import SafetyGuard


def test_block_public_ip_by_default():
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("examples.probe.portscan")
    guard = SafetyGuard()
    with pytest.raises(PermissionError):
        guard.validate_inputs(manifest, {"targets": ["8.8.8.8"]}, unsafe=False)

    # should pass in unsafe mode
    guard.validate_inputs(manifest, {"targets": ["8.8.8.8"]}, unsafe=True)