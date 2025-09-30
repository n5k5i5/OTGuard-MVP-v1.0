from pathlib import Path

from framework.core.modules.loader import ModuleLoader


def test_discover_examples():
    loader = ModuleLoader([Path("modules")])
    manifests = loader.discover()
    ids = {m["id"] for m in manifests}
    assert "examples.probe.portscan" in ids
    assert "examples.post.sysinfo" in ids
    assert "examples.aux.nmap_import" in ids