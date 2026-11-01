import socket
import struct
from typing import Dict, Any, List

from framework.core.modules.base import Module


class ModbusProbeModule(Module):
    metadata = {
        "id": "ot.probe.modbus",
        "name": "Modbus TCP Probe & Diagnostic",
        "version": "1.0.0",
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
        port = int(config.get("port", 502))
        unit_ids = config.get("unit_ids", [1])
        if isinstance(unit_ids, int):
            unit_ids = [unit_ids]
        timeout = float(config.get("timeout", 1.0))
        self.config = {
            "targets": list(targets),
            "port": port,
            "unit_ids": [int(u) for u in unit_ids],
            "timeout": timeout,
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def _build_read_holding_registers_query(self, unit_id: int, start_ref: int = 0, count: int = 1) -> bytes:
        # Modbus Application Protocol Header (MBAP):
        # Transaction ID (2 bytes), Protocol ID (2 bytes = 0), Length (2 bytes = 6), Unit ID (1 byte)
        # PDU: Function Code (1 byte = 0x03 Read Holding Registers), Reference Number (2 bytes), Word Count (2 bytes)
        tx_id = 0x0001
        proto_id = 0x0000
        length = 6
        fc = 0x03
        return struct.pack(">HHHBBHH", tx_id, proto_id, length, unit_id, fc, start_ref, count)

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        devices: Dict[str, Any] = {}

        if emulate:
            for t in self.config["targets"]:
                devices[str(t)] = {
                    "is_modbus": True,
                    "port": self.config["port"],
                    "responsive_units": self.config["unit_ids"],
                    "device_type": "Simulated PLC / RTU (Modbus TCP)",
                    "vendor": "Schneider / WAGO Emulated",
                    "sample_registers": [120, 240, 0, 1],
                }
            return {"modbus_devices": devices, "emulated": True}

        port = self.config["port"]
        timeout = self.config["timeout"]

        for t in self.config["targets"]:
            dev_info: Dict[str, Any] = {
                "is_modbus": False,
                "port": port,
                "responsive_units": [],
                "error": None,
            }
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    if s.connect_ex((t, port)) == 0:
                        dev_info["is_modbus"] = True
                        for uid in self.config["unit_ids"]:
                            query = self._build_read_holding_registers_query(uid)
                            s.sendall(query)
                            resp = s.recv(256)
                            if resp and len(resp) >= 7:
                                dev_info["responsive_units"].append(uid)
                    else:
                        dev_info["error"] = "Port closed or unreachable"
            except Exception as exc:
                dev_info["error"] = str(exc)

            devices[str(t)] = dev_info

        return {"modbus_devices": devices, "emulated": False}
