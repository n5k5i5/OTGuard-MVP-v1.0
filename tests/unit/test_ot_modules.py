import json
from pathlib import Path
from framework.core.modules.loader import ModuleLoader
from framework.core.automation.resource_runner import ResourceRunner


def test_ot_modules_discovered():
    loader = ModuleLoader([Path("modules")])
    manifests = loader.discover()
    ids = [m.get("id") for m in manifests]
    
    assert "ot.probe.modbus" in ids
    assert "ot.probe.s7comm" in ids
    assert "ot.probe.bacnet" in ids
    assert "net.probe.http_banner" in ids
    assert "util.transform.export" in ids


def test_modbus_probe_execution():
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("ot.probe.modbus")
    assert manifest is not None
    mod = loader.load_module(manifest)

    mod.validate({"targets": ["127.0.0.1"], "port": 502, "unit_ids": [1]})
    mod.prepare({"emulate": True})
    res = mod.execute()

    assert "modbus_devices" in res
    assert "127.0.0.1" in res["modbus_devices"]
    assert res["modbus_devices"]["127.0.0.1"]["is_modbus"] is True


def test_s7comm_probe_execution():
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("ot.probe.s7comm")
    assert manifest is not None
    mod = loader.load_module(manifest)

    mod.validate({"targets": "127.0.0.1"})
    mod.prepare({"emulate": True})
    res = mod.execute()

    assert "s7_devices" in res
    assert res["s7_devices"]["127.0.0.1"]["is_s7"] is True


def test_bacnet_probe_execution():
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("ot.probe.bacnet")
    assert manifest is not None
    mod = loader.load_module(manifest)

    mod.validate({"targets": ["127.0.0.1"]})
    mod.prepare({"emulate": True})
    res = mod.execute()

    assert "bacnet_devices" in res
    assert res["bacnet_devices"]["127.0.0.1"]["is_bacnet"] is True


def test_http_banner_execution():
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("net.probe.http_banner")
    assert manifest is not None
    mod = loader.load_module(manifest)

    mod.validate({"targets": ["127.0.0.1"], "ports": [80]})
    mod.prepare({"emulate": True})
    res = mod.execute()

    assert "http_banners" in res
    assert len(res["http_banners"]["127.0.0.1"]) > 0


def test_export_transform_execution(tmp_path):
    loader = ModuleLoader([Path("modules")])
    manifest = loader.get_manifest_by_id("util.transform.export")
    assert manifest is not None
    mod = loader.load_module(manifest)

    out_file = tmp_path / "test_out.json"
    mod.validate({"data": {"test_key": "test_val"}, "format": "json", "output_file": str(out_file)})
    mod.prepare({})
    res = mod.execute()

    assert res["record_count"] == 1
    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["test_key"] == "test_val"


def test_ot_comprehensive_workflow():
    loader = ModuleLoader([Path("modules")])
    runner = ResourceRunner(loader=loader, env={"emulate": True})
    spec_path = Path("resources/examples/ot_security_assessment.yaml")
    results = runner.run_file(spec_path)

    assert "modbus_step" in results
    assert "s7_step" in results
    assert "bacnet_step" in results
    assert "hmi_step" in results
    assert "export_step" in results
