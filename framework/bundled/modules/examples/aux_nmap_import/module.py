from typing import Dict, Any, List
import xml.etree.ElementTree as ET
from pathlib import Path

from framework.core.modules.base import Module


class NmapImportModule(Module):
    metadata = {
        "id": "examples.aux.nmap_import",
        "name": "Import Nmap XML (Example)",
        "version": "0.1.0",
        "type": "auxiliary",
        "safety_level": "lab",
    }

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        p = config.get("path")
        if not p:
            raise ValueError("path is required")
        path = Path(p)
        if not path.exists():
            raise FileNotFoundError(f"Nmap XML not found: {p}")
        self.config = {"path": path}

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def execute(self, session=None) -> Dict[str, Any]:
        tree = ET.parse(self.config["path"])
        root = tree.getroot()
        hosts: List[Dict[str, Any]] = []
        for host in root.findall("host"):
            addr_el = host.find("address")
            if addr_el is None:
                continue
            addr = addr_el.attrib.get("addr")
            ports_out = []
            ports = host.find("ports")
            if ports is not None:
                for p in ports.findall("port"):
                    portid = int(p.attrib.get("portid", "0"))
                    state_el = p.find("state")
                    state = state_el.attrib.get("state") if state_el is not None else "unknown"
                    service_el = p.find("service")
                    name = service_el.attrib.get("name") if service_el is not None else None
                    ports_out.append({"port": portid, "state": state, "service": name})
            hosts.append({"address": addr, "ports": ports_out})
        return {"hosts": hosts}