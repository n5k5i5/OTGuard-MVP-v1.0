import socket
from typing import Dict, Any, List

from framework.core.modules.base import Module


class BACnetProbeModule(Module):
    metadata = {
        "id": "ot.probe.bacnet",
        "name": "BACnet/IP Building Automation Probe",
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
        port = int(config.get("port", 47808))
        timeout = float(config.get("timeout", 1.0))
        self.config = {
            "targets": list(targets),
            "port": port,
            "timeout": timeout,
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def _build_who_is_packet(self) -> bytes:
        # BVLL (BACnet Virtual Link Layer):
        # 0x81 (BVLL Type), 0x0a (Original-Unicast-NPDU), 0x00, 0x0c (Length = 12 bytes)
        # NPDU: 0x01 (Version 1), 0x20 (Network Layer Message)
        # APDU: 0x10 (Unconfirmed-Request), 0x08 (Service Choice = Who-Is)
        return bytes([
            0x81, 0x0a, 0x00, 0x0c,
            0x01, 0x20, 0xff, 0xff, 0x00, 0xff,
            0x10, 0x08
        ])

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        devices: Dict[str, Any] = {}

        if emulate:
            for t in self.config["targets"]:
                devices[str(t)] = {
                    "is_bacnet": True,
                    "port": self.config["port"],
                    "protocol": "BACnet/IP (Annex J)",
                    "vendor": "Honeywell / Johnson Controls (Emulated)",
                    "device_instance": 1001,
                    "who_is_acknowledged": True,
                }
            return {"bacnet_devices": devices, "emulated": True}

        port = self.config["port"]
        timeout = self.config["timeout"]

        for t in self.config["targets"]:
            dev_info: Dict[str, Any] = {
                "is_bacnet": False,
                "port": port,
                "vendor": None,
                "error": None,
            }
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(timeout)
                    packet = self._build_who_is_packet()
                    s.sendto(packet, (t, port))
                    data, _ = s.recvfrom(512)
                    if data and len(data) >= 4 and data[0] == 0x81:
                        dev_info["is_bacnet"] = True
                        dev_info["vendor"] = "BACnet/IP Device Responded"
            except socket.timeout:
                dev_info["error"] = "No response (timeout)"
            except Exception as exc:
                dev_info["error"] = str(exc)

            devices[str(t)] = dev_info

        return {"bacnet_devices": devices, "emulated": False}
