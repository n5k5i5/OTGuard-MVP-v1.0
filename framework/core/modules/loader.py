import importlib.util
from pathlib import Path
from typing import List, Dict, Optional

import yaml

from framework.core.modules.manifest import ModuleManifest


class ModuleLoader:
    def __init__(self, search_paths: List[Path]):
        self.search_paths = search_paths

    def discover(self) -> List[Dict]:
        manifests = []
        for mp in self._find_manifest_paths():
            with open(mp, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            manifests.append(data)
        return manifests

    def get_manifest_by_id(self, module_id: str) -> Optional[ModuleManifest]:
        for mp in self._find_manifest_paths():
            with open(mp, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            if data.get("id") == module_id:
                return ModuleManifest(path=mp.parent, data=data)
        return None

    def load_module(self, manifest: ModuleManifest):
        entry = manifest.get("entry")
        if not entry or ":" not in entry:
            raise ValueError("Invalid entry in manifest. Expected 'module:ClassName'")
        module_rel, class_name = entry.split(":", 1)
        py_path = manifest.path / (module_rel.replace(".", "/") + ".py")
        if not py_path.exists():
            # allow just "module" filename
            py_path = manifest.path / (module_rel + ".py")
        if not py_path.exists():
            raise FileNotFoundError(f"Module python file not found: {py_path}")

        spec = importlib.util.spec_from_file_location(f"dynamic.{manifest.id}", py_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import module from {py_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls = getattr(mod, class_name)
        return cls()

    def _find_manifest_paths(self) -> List[Path]:
        manifests = []
        for base in self.search_paths:
            for mp in base.rglob("module.yaml"):
                manifests.append(mp)
        return manifests