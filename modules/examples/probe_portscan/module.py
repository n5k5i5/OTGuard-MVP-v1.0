import socket
from typing import Dict, Any, List

from framework.core.modules.base import Module


class PortScanModule(Module):
    metadata = {
        "id": "examples.probe.portscan",
        "name": "Port Scanner (Example)",
        "version": "0.1.0",
        "type": "probe",
        "safety_level": "lab",
    }

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        if "targets" not in config:
            raise ValueError("targets is required")
        targets = config["targets"]
        if isinstance(targets, str):
            targets = [targets]
        ports = config.get("ports", [22, 80, 443])
        if isinstance(ports, int):
            ports = [ports]
        self.config = {"targets": list(targets), "ports": list(ports)}

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        results: Dict[str, List[int]] = {}
        if emulate:
            # Deterministic synthetic results for speed and safety
            for t in self.config["targets"]:
                results[str(t)] = [p for p in self.config["ports"] if p in (22, 80)]
            return {"open_ports": results, "emulated": True}

        for t in self.config["targets"]:
            open_ports: List[int] = []
            for p in self.config["ports"]:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    try:
                        if s.connect_ex((t, int(p))) == 0:
                            open_ports.append(int(p))
                    except Exception:
                        pass
            results[str(t)] = open_ports
        return {"open_ports": results, "emulated": False}