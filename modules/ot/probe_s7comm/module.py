import socket
from typing import Dict, Any, List

from framework.core.modules.base import Module


class S7CommProbeModule(Module):
    metadata = {
        "id": "ot.probe.s7comm",
        "name": "Siemens S7comm / ISO-on-TCP Probe",
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
        port = int(config.get("port", 102))
        timeout = float(config.get("timeout", 1.0))
        self.config = {
            "targets": list(targets),
            "port": port,
            "timeout": timeout,
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def _build_cotp_connection_request(self) -> bytes:
        # TPKT (RFC 1006): version 3, reserved 0, length 22
        # COTP: length 17, type 0xE0 (Connection Request), dst 0x0000, src 0x0100, class 0
        # TSAP source (0x0100), TSAP destination (0x0102 - Rack 0, Slot 2)
        return bytes([
            0x03, 0x00, 0x00, 0x16,  # TPKT
            0x11,                    # COTP Length
            0xe0,                    # COTP Connection Request
            0x00, 0x00,              # Dst Ref
            0x01, 0x00,              # Src Ref
            0x00,                    # Class & Option
            0xc1, 0x02, 0x01, 0x00,  # Parameter: Src-TSAP
            0xc2, 0x02, 0x01, 0x02,  # Parameter: Dst-TSAP (Rack 0, Slot 2)
            0xc0, 0x01, 0x0a         # Parameter: TPDU Size
        ])

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        devices: Dict[str, Any] = {}

        if emulate:
            for t in self.config["targets"]:
                devices[str(t)] = {
                    "is_s7": True,
                    "port": self.config["port"],
                    "plc_type": "Siemens Simatic S7-1200 / S7-1500 (Emulated)",
                    "module_rack_slot": "Rack 0, Slot 2",
                    "cotp_established": True,
                    "fingerprint": "6ES7 214-1AG40-0XB0 v4.2",
                }
            return {"s7_devices": devices, "emulated": True}

        port = self.config["port"]
        timeout = self.config["timeout"]

        for t in self.config["targets"]:
            dev_info: Dict[str, Any] = {
                "is_s7": False,
                "port": port,
                "cotp_established": False,
                "plc_type": None,
                "error": None,
            }
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    if s.connect_ex((t, port)) == 0:
                        s.sendall(self._build_cotp_connection_request())
                        resp = s.recv(1024)
                        # Check TPKT (0x03) and COTP Connection Confirm (0xD0)
                        if resp and len(resp) >= 6 and resp[0] == 0x03 and resp[5] == 0xd0:
                            dev_info["is_s7"] = True
                            dev_info["cotp_established"] = True
                            dev_info["plc_type"] = "Siemens S7 PLC (COTP Confirmed)"
                    else:
                        dev_info["error"] = "Port closed or unreachable"
            except Exception as exc:
                dev_info["error"] = str(exc)

            devices[str(t)] = dev_info

        return {"s7_devices": devices, "emulated": False}
